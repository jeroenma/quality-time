import {
    useArrayURLSearchQuery,
    useBooleanURLSearchQuery,
    useIntegerURLSearchQuery,
    useStringURLSearchQuery
} from './hooks/url_search_query';

function urlSearchQueryKey(key, report_uuid) {
    // Make the settings changeable per report (and separately for the reports overview) by adding the report UUID as
    // postfix to the settings key:
    return key + (report_uuid ? `_${report_uuid}` : "")
}

export function useDateIntervalURLSearchQuery(report_uuid, defaultValue = 7) {
    return useIntegerURLSearchQuery(urlSearchQueryKey("date_interval", report_uuid), defaultValue);
}

export function useDateOrderURLSearchQuery(report_uuid, defaultValue = "descending") {
    return useStringURLSearchQuery(urlSearchQueryKey("date_order", report_uuid), defaultValue);
}

export function useHiddenColumnsURLSearchQuery(report_uuid) {
    return useArrayURLSearchQuery(urlSearchQueryKey("hidden_columns", report_uuid));
}

export function useHiddenTagsURLSearchQuery(report_uuid) {
    return useArrayURLSearchQuery(urlSearchQueryKey("hidden_tags", report_uuid));
}

export function useMetricsToHideURLSearchQuery(report_uuid, defaultValue = "none") {
    return useStringURLSearchQuery(urlSearchQueryKey("metrics_to_hide", report_uuid), defaultValue);
}

export function useNrDatesURLSearchQuery(report_uuid, defaultValue = 1) {
    return useIntegerURLSearchQuery(urlSearchQueryKey("nr_dates", report_uuid), defaultValue);
}

export function useSortColumnURLSearchQuery(report_uuid, defaultValue = "") {
    return useStringURLSearchQuery(urlSearchQueryKey("sort_column", report_uuid), defaultValue);
}

export function useSortDirectionURLSearchQuery(report_uuid, defaultValue = "ascending") {
    return useStringURLSearchQuery(urlSearchQueryKey("sort_direction", report_uuid), defaultValue);
}

export function useVisibleDetailsTabsSearchQuery(report_uuid) {
    return useArrayURLSearchQuery(urlSearchQueryKey("tabs", report_uuid));
}

export function useShowIssueSummaryURLSearchQuery(report_uuid) {
    return useBooleanURLSearchQuery(urlSearchQueryKey("show_issue_summary", report_uuid));
}

export function useShowIssueCreationDateURLSearchQuery(report_uuid) {
    return useBooleanURLSearchQuery(urlSearchQueryKey("show_issue_creation_date", report_uuid));
}

export function useShowIssueUpdateDateURLSearchQuery(report_uuid) {
    return useBooleanURLSearchQuery(urlSearchQueryKey("show_issue_update_date", report_uuid));
}

export function useShowIssueDueDateURLSearchQuery(report_uuid) {
    return useBooleanURLSearchQuery(urlSearchQueryKey("show_issue_due_date", report_uuid));
}

export function useShowIssueReleaseURLSearchQuery(report_uuid) {
    return useBooleanURLSearchQuery(urlSearchQueryKey("show_issue_release", report_uuid));
}

export function useShowIssueSprintURLSearchQuery(report_uuid) {
    return useBooleanURLSearchQuery(urlSearchQueryKey("show_issue_sprint", report_uuid));
}

export function useSettings(report_uuid) {
    return {
        dateInterval: useDateIntervalURLSearchQuery(report_uuid),
        dateOrder: useDateOrderURLSearchQuery(report_uuid),
        hiddenColumns: useHiddenColumnsURLSearchQuery(report_uuid),
        hiddenTags: useHiddenTagsURLSearchQuery(report_uuid),
        metricsToHide: useMetricsToHideURLSearchQuery(report_uuid, report_uuid === "" ? "all" : "none"),
        nrDates: useNrDatesURLSearchQuery(report_uuid),
        showIssueSummary: useShowIssueSummaryURLSearchQuery(report_uuid),
        showIssueCreationDate: useShowIssueCreationDateURLSearchQuery(report_uuid),
        showIssueUpdateDate: useShowIssueUpdateDateURLSearchQuery(report_uuid),
        showIssueDueDate: useShowIssueDueDateURLSearchQuery(report_uuid),
        showIssueRelease: useShowIssueReleaseURLSearchQuery(report_uuid),
        showIssueSprint: useShowIssueSprintURLSearchQuery(report_uuid),
        sortColumn: useSortColumnURLSearchQuery(report_uuid),
        sortDirection: useSortDirectionURLSearchQuery(report_uuid),
        visibleDetailsTabs: useVisibleDetailsTabsSearchQuery(report_uuid)
    }
}