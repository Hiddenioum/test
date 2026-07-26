/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#include "core/core_settings.h"

#include "base/qt/qt_common_supports.h"

namespace Core {

Settings::Settings() = default;

void Settings::setPausedForUi(bool paused) {
	_pausedForUi = paused;
}

bool Settings::pausedForUi() const {
	return _pausedForUi;
}

void Settings::setSilentForUi(bool silent) {
	_silentForUi = silent;
}

bool Settings::silentForUi() const {
	return _silentForUi;
}

} // namespace Core
