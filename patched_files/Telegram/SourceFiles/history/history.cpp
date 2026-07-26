/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#include "history/history.h"

namespace History {

void History::setGhostModeActive(bool active) {
	_ghostModeActive = active;
}

bool History::ghostModeActive() const {
	return _ghostModeActive;
}

} // namespace History
