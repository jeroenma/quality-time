import { string } from "prop-types"
import { Message } from "semantic-ui-react"

import { datePropType, optionalDatePropType } from "../sharedPropTypes"

function ErrorMessage({ children }) {
    return (
        <Message warning size="huge">
            <Message.Header>{children}</Message.Header>
        </Message>
    )
}
ErrorMessage.propTypes = {
    children: string,
}

export function ReportErrorMessage({ reportDate }) {
    return (
        <ErrorMessage>
            {reportDate ? `Sorry, this report didn't exist at ${reportDate}` : "Sorry, this report doesn't exist"}
        </ErrorMessage>
    )
}
ReportErrorMessage.propTypes = {
    reportDate: optionalDatePropType,
}

export function ReportsOverviewErrorMessage({ reportDate }) {
    return <ErrorMessage>{`Sorry, no reports existed at ${reportDate}`}</ErrorMessage>
}
ReportsOverviewErrorMessage.propTypes = {
    reportDate: datePropType,
}
