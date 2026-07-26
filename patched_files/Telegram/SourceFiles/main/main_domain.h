/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#pragma once

namespace Main {

class Domain {
public:
	void setAccountPaused(not_null<Account*> account, bool paused);
	void setAccountSilent(not_null<Account*> account, bool silent);
};

} // namespace Main
