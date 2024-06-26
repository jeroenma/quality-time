import "./FocusableTab.css"

import { useContext } from "react"

import { DarkMode } from "../context/DarkMode"
import { childrenPropType } from "../sharedPropTypes"

export function FocusableTab(props) {
    const className = useContext(DarkMode) ? "tabbutton inverted" : "tabbutton"
    return <button className={className}>{props.children}</button>
}
FocusableTab.propTypes = {
    children: childrenPropType,
}
