/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#include "history/view/history_view_top_bar_widget.h"
#include "history/history.h"

namespace HistoryView {

void TopBarWidget::paintTopBar(Painter &p) {
	if (const auto history = _activeChat.key.owningHistory()) {
		if (history->ghostModeActive()) {
			p.setFont(st::dialogsTextFont);
			p.setPen(st::dialogsNameFg);
			p.drawText(nameleft + namewidth - 80, nametop, u"👻 Ghost"_q);
		}
	}
}

} // namespace HistoryView
