import { fireEvent, render, renderHook, screen } from "@testing-library/react"
import history from "history/browser"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { useHiddenTagsURLSearchQuery } from "../app_ui_settings"
import { DataModel } from "../context/DataModel"
import { mockGetAnimations } from "../dashboard/MockAnimations"
import { ReportDashboard } from "./ReportDashboard"

beforeEach(() => {
    mockGetAnimations()
    history.push("")
})

const dataModel = {
    metrics: {
        metric_type: { default_scale: "count" },
    },
}

const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            name: "Subject title",
            metrics: {
                metric_uuid: { type: "metric_type", tags: ["tag"], recent_measurements: [] },
                another_metric_uuid: {
                    type: "metric_type",
                    tags: ["other"],
                    recent_measurements: [],
                },
            },
        },
    },
}

function renderDashboard({ hiddenTags = null, dates = [new Date()], onClick = jest.fn(), reportToRender = null } = {}) {
    let settings = createTestableSettings()
    if (hiddenTags) {
        settings.hiddenTags = hiddenTags
    }
    return render(
        <DataModel.Provider value={dataModel}>
            <div id="dashboard">
                <ReportDashboard dates={dates} onClick={onClick} report={reportToRender} settings={settings} />
            </div>
        </DataModel.Provider>,
    )
}

it("shows the dashboard", async () => {
    renderDashboard({ reportToRender: report })
    expect(screen.getAllByText(/Subject title/).length).toBe(1)
    expect(screen.getAllByText(/Legend/).length).toBe(1)
    expect(screen.getAllByText(/tag/).length).toBe(1)
    expect(screen.getAllByText(/other/).length).toBe(1)
})

it("hides tags", async () => {
    history.push("?hidden_tags=other")
    const hiddenTags = renderHook(() => useHiddenTagsURLSearchQuery())
    renderDashboard({ reportToRender: report, hiddenTags: hiddenTags.result.current })
    expect(screen.getAllByText(/Subject title/).length).toBe(1)
    expect(screen.getAllByText(/tag/).length).toBe(1)
    expect(screen.queryAllByText(/other/).length).toBe(0)
})

it("hides a subject if all its tags are hidden", async () => {
    history.push("?hidden_tags=other,tag")
    const hiddenTags = renderHook(() => useHiddenTagsURLSearchQuery())
    renderDashboard({ reportToRender: report, hiddenTags: hiddenTags.result.current })
    expect(screen.queryAllByText(/Subject title/).length).toBe(0)
    expect(screen.queryAllByText(/tag/).length).toBe(0)
    expect(screen.queryAllByText(/other/).length).toBe(0)
})

it("calls the callback on click", async () => {
    const onClick = jest.fn()
    renderDashboard({ reportToRender: report, onClick: onClick })
    fireEvent.click(screen.getByText(/Subject title/))
    expect(onClick).toHaveBeenCalledWith(expect.anything(), "subject_uuid")
})

it("hides the subject cards", async () => {
    history.push("?hidden_cards=subjects")
    renderDashboard({ reportToRender: report })
    expect(screen.queryAllByText(/Subject title/).length).toBe(0)
    expect(screen.getAllByText(/tag/).length).toBe(1)
    expect(screen.getAllByText(/other/).length).toBe(1)
})

it("hides the tag cards", async () => {
    history.push("?hidden_cards=tags")
    renderDashboard({ reportToRender: report })
    expect(screen.getAllByText(/Subject title/).length).toBe(1)
    expect(screen.queryAllByText(/tag/).length).toBe(0)
    expect(screen.queryAllByText(/other/).length).toBe(0)
})
