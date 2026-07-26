/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#include "data/data_histories.h"

#include "data/data_history_messages.h"
#include "data/data_channel.h"
#include "data/data_user.h"
#include "data/data_chat.h"
#include "data/data_folder.h"
#include "data/data_session.h"
#include "history/history.h"
#include "history/history_item.h"
#include "main/main_session.h"
#include "apiwrap.h"

namespace Data {

Histories::Histories(not_null<Session*> owner)
: _owner(owner) {
}

Histories::~Histories() = default;

void Histories::sendReadRequests() {
	for (auto &[history, state] : _readRequests) {
		if (state.willReadTill > state.sentReadTill) {
			sendReadRequest(history, state);
		}
	}
}

void Histories::sendReadRequest(not_null<History*> history, State &state) {
	if (history->ghostModeActive()) {
		state.willReadTill = 0;
		state.willReadWhen = 0;
		return;
	}
	Expects(state.willReadTill > state.sentReadTill);

	const auto tillId = state.sentReadTill = base::take(state.willReadTill);
	const auto peer = history->peer;
	if (const auto channel = peer->asChannel()) {
		_owner->api().request(MTPchannels_ReadHistory(
			channel->inputChannel,
			MTP_int(tillId)
		)).done([=] {
			readContents(history, tillId);
		}).send();
	} else {
		_owner->api().request(MTPmessages_ReadHistory(
			peer->input,
			MTP_int(tillId)
		)).done([=](const MTPmessages_AffectedMessages &result) {
			_owner->api().applyAffectedMessages(peer, result);
			readContents(history, tillId);
		}).send();
	}
}

void Histories::readContents(not_null<History*> history, MsgId tillId) {
}

} // namespace Data
