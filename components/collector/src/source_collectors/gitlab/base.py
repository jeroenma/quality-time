"""GitLab collector base classes."""

from abc import ABC
from datetime import date, datetime, timedelta
from typing import cast

from shared.utils.date_time import now

from base_collectors import SourceCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL, Job
from model import Entities, Entity, SourceResponses


class GitLabBase(SourceCollector, ABC):
    """Base class for GitLab collectors."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to follow GitLab pagination links, if necessary."""
        all_responses = responses = await super()._get_source_responses(*urls)
        while next_urls := await self._next_urls(responses):
            # Retrieving consecutive big responses without reading the response hangs the client, see
            # https://github.com/aio-libs/aiohttp/issues/2217
            for response in responses:
                await response.read()
            all_responses.extend(responses := await super()._get_source_responses(*next_urls))
        return all_responses

    def _basic_auth_credentials(self) -> tuple[str, str] | None:
        """Override to return None, as the private token is passed as header."""
        return None

    def _headers(self) -> dict[str, str]:
        """Extend to add the private token, if any, to the headers."""
        headers = super()._headers()
        if private_token := self._parameter("private_token"):
            headers["Private-Token"] = str(private_token)
        return headers

    async def _next_urls(self, responses: SourceResponses) -> list[URL]:
        """Return the next (pagination) links from the responses."""
        return [URL(next_url) for response in responses if (next_url := response.links.get("next", {}).get("url"))]


class GitLabProjectBase(GitLabBase, ABC):
    """Base class for GitLab collectors for a specific project."""

    async def _gitlab_api_url(self, api: str) -> URL:
        """Return a GitLab API url for a project, if present in the parameters."""
        url = await super()._api_url()
        project = self._parameter("project", quote=True)
        api_url = f"{url}/api/v4/projects/{project}" + (f"/{api}" if api else "")
        sep = "&" if "?" in api_url else "?"
        api_url += f"{sep}per_page=100"
        return URL(api_url)


class GitLabJobsBase(GitLabProjectBase):
    """Base class for GitLab job collectors."""

    async def _api_url(self) -> URL:
        """Override to return the jobs API."""
        return await self._gitlab_api_url("jobs")

    async def _next_urls(self, responses: SourceResponses) -> list[URL]:
        """Return the next (pagination) links from the responses as long as we're within lookback days."""
        # Note: the GitLab documentation (https://docs.gitlab.com/ee/api/jobs.html#list-project-jobs) says:
        # "Jobs are sorted in descending order of their IDs." The API has no query parameters to sort jobs by date
        # created or by date run, so we're going to assume that descending order of IDs is roughly equal to descending
        # order of date created and date run. As soon as all jobs on a page have a build date that is outside the
        # lookback period we stop the pagination.
        today = now().date()
        lookback_date = today - timedelta(days=int(cast(str, self._parameter("lookback_days"))))
        for response in responses:
            for job in await response.json():
                if self._build_date(job) > lookback_date:
                    return await super()._next_urls(responses)
        return []

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the jobs from the responses."""
        return Entities(
            [
                Entity(
                    key=job["id"],
                    name=job["name"],
                    url=job["web_url"],
                    build_status=job["status"],
                    branch=job["ref"],
                    stage=job["stage"],
                    build_date=str(self._build_date(job)),
                )
                for job in await self._jobs(responses)
            ],
        )

    @staticmethod
    async def _jobs(responses: SourceResponses) -> list[Job]:
        """Return the jobs to count."""

        def newer(job1: Job, job2: Job) -> Job:
            """Return the newer of the two jobs."""
            return job1 if job1["created_at"] > job2["created_at"] else job2

        jobs: dict[tuple[str, str, str], Job] = {}
        for response in responses:
            for job in await response.json():
                key = job["name"], job["stage"], job["ref"]
                jobs[key] = newer(job, jobs.get(key, job))
        return list(jobs.values())

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to count the job."""
        return not match_string_or_regular_expression(
            entity["name"],
            self._parameter("jobs_to_ignore"),
        ) and not match_string_or_regular_expression(entity["branch"], self._parameter("refs_to_ignore"))

    @staticmethod
    def _build_date(job: Job) -> date:
        """Return the build date of the job."""
        return parse_datetime(job.get("finished_at") or job["created_at"]).date()


class GitLabPipelineBase(GitLabProjectBase):
    """Base class for GitLab pipeline collectors."""

    async def _api_url(self) -> URL:
        """Override to return the pipeline API."""
        lookback_date = (now() - timedelta(days=int(cast(str, self._parameter("lookback_days"))))).date()
        return await self._gitlab_api_url(f"pipelines?updated_after={lookback_date}")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to return a landing URL for the most recent pipeline."""
        urls = []
        try:
            for response in responses:
                pipelines = await response.json()
                urls.extend(
                    [
                        (self._datetime(pipeline), pipeline["web_url"])
                        for pipeline in pipelines
                        if self._include_pipeline(pipeline)
                    ],
                )
        except StopAsyncIteration:
            pass
        return max(urls, default=(None, await super()._landing_url(responses)))[1]

    def _include_pipeline(self, pipeline) -> bool:
        """Return whether this pipeline should be considered."""
        return (
            pipeline["ref"] == self._parameter("branch")
            and pipeline["status"] in self._parameter("pipeline_statuses_to_include")
            and pipeline["source"] in self._parameter("pipeline_triggers_to_include")
        )

    @staticmethod
    def _datetime(pipeline) -> datetime:
        """Return the datetime of the pipeline."""
        return parse_datetime(pipeline.get("updated_at") or pipeline["created_at"])
