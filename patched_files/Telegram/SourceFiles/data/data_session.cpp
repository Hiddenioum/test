/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#include "data/data_session.h"

#include "data/data_history_messages.h"
#include "history/history.h"
#include "history/history_item.h"

namespace Data {

Session::Session(not_null<Main::Session*> session)
: _session(session) {
}

Session::~Session() = default;

void Session::processMessagesDeleted(const std.vector<MsgId> &ids) {
	std::vector<not_null<HistoryItem*>> toDestroy;
	std::set<not_null<History*>> historiesToCheck;

	for (const auto id : ids) {
		if (const auto item = message(id)) {
			historiesToCheck.insert(item->history());
			toDestroy.push_back(item);
		}
	}
	if (!toDestroy.empty()) {
		for (const auto &item : toDestroy) {
			item->setLocallyDeleted(true);
		}
	}
}

} // namespace Data
