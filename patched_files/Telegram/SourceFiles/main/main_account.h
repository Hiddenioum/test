/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#pragma once

namespace Main {

class Account {
public:
	void setPausedForUi(bool paused);
	void setSilentForUi(bool silent);
	[[nodiscard]] bool pausedForUi() const;
	[[nodiscard]] bool silentForUi() const;
};

} // namespace Main
