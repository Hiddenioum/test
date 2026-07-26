/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#pragma once

#include "data/data_peer.h"

class History {
public:
	void setGhostModeActive(bool active) { _ghostModeActive = active; }
	[[nodiscard]] bool ghostModeActive() const { return _ghostModeActive; }

private:
	bool _ghostModeActive = false;
};
