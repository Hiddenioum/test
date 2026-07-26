/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#pragma once

#include "history/history.h"
#include "data/data_peer.h"

class HistoryItem {
public:
	[[nodiscard]] bool locallyDeleted() const { return _locallyDeleted; }
	void setLocallyDeleted(bool deleted) { _locallyDeleted = deleted; }

private:
	bool _locallyDeleted = false;
};
