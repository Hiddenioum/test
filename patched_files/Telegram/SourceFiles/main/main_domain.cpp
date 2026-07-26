/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#include "main/main_domain.h"
#include "main/main_account.h"

namespace Main {

void Domain::setAccountPaused(not_null<Account*> account, bool paused) {
	account->setPausedForUi(paused);
}

void Domain::setAccountSilent(not_null<Account*> account, bool silent) {
	account->setSilentForUi(silent);
}

} // namespace Main
