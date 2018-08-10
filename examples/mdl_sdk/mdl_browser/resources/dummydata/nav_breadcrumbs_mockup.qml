import QtQuick 2.10
import QtQuick.Controls 2.3
import QtQuick.Controls.Universal 2.3
import QtQuick.Layouts 1.3

ListModel {

    ListElement {
        packageName: "root"
        packageShortMode: false
    }

    ListElement {
        packageName: "First"
        packageShortMode: true
    }

    ListElement {
        packageName: "Second"
        packageShortMode: false
    }

    ListElement {
        packageName: "Third"
        packageShortMode: false
    }

    ListElement {
        packageName: "Fourth"
        packageShortMode: false
    }

    ListElement {
        packageName: "Fifth"
        packageShortMode: false
    }
} 