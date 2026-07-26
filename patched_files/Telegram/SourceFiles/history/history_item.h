/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#pragma once

class HistoryItem {
public:
	[[nodiscard]] bool locallyDeleted() const;
	void setLocallyDeleted(bool deleted);

private:
	bool _locallyDeleted = false;
};
