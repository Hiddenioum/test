/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#include "dialogs/dialogs_inner_widget.h"

#include "history/history.h"
#include "data/data_histories.h"

namespace Dialogs {

void InnerWidget::mousePressReleased(Qt::MouseButton button, Qt::KeyboardModifiers modifiers, bool pressed) {
	if (button == Qt::LeftButton) {
		if ((modifiers & Qt::ControlModifier) && (modifiers & Qt::AltModifier) && pressed) {
			if (const auto history = _pressed ? _pressed->history() : nullptr) {
				history->setGhostModeActive(true);
			}
		}
	}
}

} // namespace Dialogs
