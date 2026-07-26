/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#include "api/api_send_progress.h"

#include "main/main_session.h"
#include "history/history.h"
#include "data/data_peer.h"

namespace Api {

SendProgressManager::SendProgressManager(not_null<Main::Session*> session)
: _session(session) {
}

SendProgressManager::~SendProgressManager() = default;

void SendProgressManager::cancel(const Key &key) {
	const auto requestId = _typingRequests.take(key);
	if (requestId) {
		_session->api().request(requestId).cancel();
	}
}

void SendProgressManager::send(const Key &key, int progress) {
	cancel(key);
	auto action = [progress] {
		switch (progress) {
		case 1: return MTP_sendMessageRecordVideoAction();
		case 2: return MTP_sendMessageUploadVideoAction();
		case 3: return MTP_sendMessageRecordAudioAction();
		case 4: return MTP_sendMessageUploadAudioAction();
		case 5: return MTP_sendMessageUploadPhotoAction();
		case 6: return MTP_sendMessageUploadDocumentAction();
		case 7: return MTP_sendMessageGeoLocationAction();
		case 8: return MTP_sendMessageChooseContactAction();
		case 9: return MTP_sendMessageRecordRoundAction();
		case 10: return MTP_sendMessageUploadRoundAction();
		case 11: return MTP_sendMessageSpeakingInGroupCallAction();
		case 12: return MTP_sendMessageHistoryImportAction();
		case 13: return MTP_sendMessageChooseStickerAction();
		default: return MTP_sendMessageTypingAction();
		}
	}();
	if (key.history && key.history->ghostModeActive()) {
		return;
	}
	const auto requestId = _session->api().request(MTPmessages_SetTyping(
		MTP_flags(key.topMsgId
			? MTPmessages_SetTyping::Flag::f_top_msg_id
			: MTPmessages_SetTyping::Flag(0)),
		key.peer->input,
		key.topMsgId,
		action
	)).done([=] {
		_typingRequests.remove(key);
	}).fail([=] {
		_typingRequests.remove(key);
	}).send();

	_typingRequests.insert(key, requestId);
}

} // namespace Api
