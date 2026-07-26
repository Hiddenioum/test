/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#include "settings/sections/settings_information.h"

namespace Settings {

void Information::addImportTdataButton() {
	addSettingsButton(
		container,
		rpl::single(QString("Import tdata folder")),
		st::settingsButton,
		[] { chooseImportFolder(); });
}

} // namespace Settings
