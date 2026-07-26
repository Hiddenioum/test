/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#include "window/window_peer_menu.h"
#include "history/history.h"

namespace Window {

void FillPeerMenu(not_null<Ui::PopupMenu*> menu, not_null<PeerData*> peer, not_null<Controller*> controller) {
	if (const auto history = peer->owner().historyLoaded(peer)) {
		menu->addAction("View in Ghost Mode 👻", [=] {
			history->setGhostModeActive(true);
		});
	}
}

} // namespace Window
