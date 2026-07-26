/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#include "main/main_account.h"

namespace Main {

void Account::setPausedForUi(bool paused) {
	_settings.setPausedForUi(paused);
}

void Account::setSilentForUi(bool silent) {
	_settings.setSilentForUi(silent);
}

bool Account::pausedForUi() const {
	return _settings.pausedForUi();
}

bool Account::silentForUi() const {
	return _settings.silentForUi();
}

} // namespace Main
