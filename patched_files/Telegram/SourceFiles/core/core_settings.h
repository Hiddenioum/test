/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#pragma once

#include "base/flags.h"

namespace Core {

class Settings final {
public:
	Settings();

	void setPausedForUi(bool paused);
	[[nodiscard]] bool pausedForUi() const;
	void setSilentForUi(bool silent);
	[[nodiscard]] bool silentForUi() const;

private:
	bool _pausedForUi = false;
	bool _silentForUi = false;

};

} // namespace Core
