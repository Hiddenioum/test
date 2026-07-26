/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#include "history/history_item.h"
#include "history/history_item_components.h"

bool HistoryItem::locallyDeleted() const {
	return _locallyDeleted;
}

void HistoryItem::setLocallyDeleted(bool deleted) {
	_locallyDeleted = deleted;
}

void HistoryItem::applyEdition(HistoryMessageEdition &&edition) {
	_text = edition.text;
	if (!Has<HistoryMessageEditRevisions>()) {
		AddComponents(HistoryMessageEditRevisions::Bit());
	}
	auto revisions = Get<HistoryMessageEditRevisions>();
	revisions->list.push_back(EditRevision{
		.text = _text,
		.date = edition.editDate,
		.hadMedia = (_media != nullptr),
	});
}
