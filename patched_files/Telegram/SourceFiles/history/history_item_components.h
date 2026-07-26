/*
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please see LEGAL file in the code repository.
*/
#pragma once

#include <vector>
#include <QString>

struct EditRevision {
	QString text;
	int date = 0;
	bool hadMedia = false;
};

struct HistoryMessageEditRevisions {
	std::vector<EditRevision> list;
};
