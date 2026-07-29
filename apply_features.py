#!/usr/bin/env python3
import os
import sys

def patch_file(filepath, target, replacement):
    if not os.path.exists(filepath):
        print(f"Skipping missing file: {filepath}")
        return False
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if target not in content:
        raise RuntimeError(f"Target string not found in {filepath}: {repr(target[:80])}")
    content = content.replace(target, replacement, 1)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Patched {filepath} successfully.")
    return True

def main():
    print("Applying custom features for Telegram Desktop v7.0.5...")

    # =========================================================================
    # 1. Ghost Mode: Block typing indicators
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/api/api_send_progress.cpp",
        "#include \"api/api_send_progress.h\"",
        "#include \"api/api_send_progress.h\"\n#include \"core/application.h\"\n#include \"core/core_settings.h\""
    )
    patch_file(
        "Telegram/SourceFiles/api/api_send_progress.cpp",
        "\tconst auto requestId = _session->api().request(MTPmessages_SetTyping(",
        "\tif ((key.history && key.history->ghostModeActive()) || Core::App().settings().globalGhostMode()) {\n\t\treturn;\n\t}\n\tconst auto requestId = _session->api().request(MTPmessages_SetTyping("
    )

    # =========================================================================
    # 2. Core Settings: Ghost Mode, Silent, Paused globals
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/core/core_settings.h",
        "\tvoid setLoopAnimatedStickers(bool value) {\n\t\t_loopAnimatedStickers = value;\n\t}",
        "\tvoid setLoopAnimatedStickers(bool value) {\n\t\t_loopAnimatedStickers = value;\n\t}\n\tvoid setGlobalGhostMode(bool ghost) { _globalGhostMode = ghost; }\n\t[[nodiscard]] bool globalGhostMode() const { return _globalGhostMode; }"
    )
    patch_file(
        "Telegram/SourceFiles/core/core_settings.h",
        "\tbool _loopAnimatedStickers = true;",
        "\tbool _loopAnimatedStickers = true;\n\tbool _globalGhostMode = false;"
    )

    # =========================================================================
    # 3. Ghost Mode: Block read receipts
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/data/data_histories.cpp",
        "#include \"core/application.h\"",
        "#include \"core/application.h\"\n#include \"core/core_settings.h\""
    )
    patch_file(
        "Telegram/SourceFiles/data/data_histories.cpp",
        "void Histories::sendReadRequest(not_null<History*> history, State &state) {",
        "void Histories::sendReadRequest(not_null<History*> history, State &state) {\n\tif (history->ghostModeActive() || Core::App().settings().globalGhostMode()) {\n\t\tstate.willReadTill = 0;\n\t\tstate.willReadWhen = 0;\n\t\treturn;\n\t}"
    )

    # =========================================================================
    # 4. Anti-Delete: Preserve locally deleted messages (set flag only)
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/data/data_session.cpp",
        "\tfor (const auto &messageId : data) {\n\t\tconst auto i = list ? list->find(messageId.v) : Messages::iterator();\n\t\tif (list && i != list->end()) {\n\t\t\tconst auto history = i->second->history();\n\t\t\ttoDestroy.push_back(i->second);\n\t\t\thistoriesToCheck.emplace(history);\n\t\t} else if (affected) {\n\t\t\taffected->unknownMessageDeleted(messageId.v);\n\t\t}\n\t}",
        "\tfor (const auto &messageId : data) {\n\t\tif (const auto item = message(peerId, messageId.v)) {\n\t\t\titem->setLocallyDeleted(true);\n\t\t}\n\t}"
    )
    patch_file(
        "Telegram/SourceFiles/data/data_session.cpp",
        "void Session::processNonChannelMessagesDeleted(const QVector<MTPint> &data) {",
        "void Session::processNonChannelMessagesDeleted(const QVector<MTPint> &data) {\n\tfor (const auto &messageId : data) {\n\t\tif (const auto item = nonChannelMessage(messageId.v)) {\n\t\t\titem->setLocallyDeleted(true);\n\t\t}\n\t}\n\treturn;"
    )

    # =========================================================================
    # 5. Ghost Mode: Per-chat methods on History
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/history/history.cpp",
        "#include \"core/ui_integration.h\"",
        "#include \"core/ui_integration.h\"\n#include \"core/core_settings.h\""
    )
    patch_file(
        "Telegram/SourceFiles/history/history.cpp",
        "History::~History() = default;",
        "History::~History() = default;\n\nvoid History::setGhostModeActive(bool active) {\n\t_ghostModeActive = active;\n}\n\nbool History::ghostModeActive() const {\n\treturn _ghostModeActive || Core::App().settings().globalGhostMode();\n}"
    )
    patch_file(
        "Telegram/SourceFiles/history/history.h",
        "\tData::Folder *folder() const override;",
        "\tData::Folder *folder() const override;\n\n\tvoid setGhostModeActive(bool active);\n\t[[nodiscard]] bool ghostModeActive() const;"
    )
    patch_file(
        "Telegram/SourceFiles/history/history.h",
        "\tstd::optional<Data::Folder*> _folder;",
        "\tstd::optional<Data::Folder*> _folder;\n\tbool _ghostModeActive = false;"
    )

    # =========================================================================
    # 6. HistoryItem: locallyDeleted flag + edit toggle fields (header)
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/history/history_item.h",
        "\t[[nodiscard]] bool out() const {",
        "\t[[nodiscard]] bool locallyDeleted() const {\n\t\treturn _locallyDeleted;\n\t}\n\tvoid setLocallyDeleted(bool deleted);\n\tvoid toggleOriginalEditVersion();\n\n\t[[nodiscard]] bool out() const {"
    )
    patch_file(
        "Telegram/SourceFiles/history/history_item.h",
        "\tMsgId id;",
        "\tMsgId id;\n\tbool _locallyDeleted = false;\n\tTextWithEntities _originalEditText;\n\tTextWithEntities _editedCurrentText;\n\tbool _showingOriginal = false;"
    )

    # =========================================================================
    # 7. HistoryItem: setLocallyDeleted (flag + resize), toggleOriginalEditVersion
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/history/history_item.cpp",
        "HistoryItem::~HistoryItem() {",
        "void HistoryItem::setLocallyDeleted(bool deleted) {\n\tif (_locallyDeleted != deleted) {\n\t\t_locallyDeleted = deleted;\n\t\thistory()->owner().requestItemResize(this);\n\t}\n}\n\nvoid HistoryItem::toggleOriginalEditVersion() {\n\tif (_originalEditText.text.isEmpty()) {\n\t\treturn;\n\t}\n\t_showingOriginal = !_showingOriginal;\n\tif (_showingOriginal) {\n\t\tsetText(_originalEditText);\n\t} else {\n\t\tsetText(_editedCurrentText);\n\t}\n\thistory()->owner().requestItemResize(this);\n}\n\nHistoryItem::~HistoryItem() {"
    )

    # Save original text in applyEdition BEFORE the edit is applied
    patch_file(
        "Telegram/SourceFiles/history/history_item.cpp",
        "\tconst auto &checkedMedia = updatingSavedLocalEdit",
        "\tif (_originalEditText.text.isEmpty()) {\n\t\t_originalEditText = originalText();\n\t}\n\tconst auto &checkedMedia = updatingSavedLocalEdit"
    )

    # Save edited text AFTER setText in applyEdition
    patch_file(
        "Telegram/SourceFiles/history/history_item.cpp",
        "\t} else {\n\t\tsetText(std::move(updatedText));\n\t\taddToSharedMediaIndex();\n\t}\n\tif (mediaCheck == MediaCheckResult::Unsupported) {",
        "\t} else {\n\t\tsetText(std::move(updatedText));\n\t\t_editedCurrentText = originalText();\n\t\taddToSharedMediaIndex();\n\t}\n\tif (mediaCheck == MediaCheckResult::Unsupported) {"
    )

    # =========================================================================
    # 8. BottomInfo: Add Deleted flag to enum
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/history/view/history_view_bottom_info.h",
        "\t\t\tEphemeral      = 0x1000,",
        "\t\t\tEphemeral      = 0x1000,\n\t\t\tDeleted        = 0x2000,"
    )

    # =========================================================================
    # 9. BottomInfo: Set Deleted flag in BottomInfoDataFromMessage
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/history/view/history_view_bottom_info.cpp",
        "\tif (const auto views = item->Get<HistoryMessageViews>()) {",
        "\tif (item->locallyDeleted()) {\n\t\tresult.flags |= Flag::Deleted;\n\t}\n\tif (const auto views = item->Get<HistoryMessageViews>()) {"
    )

    # =========================================================================
    # 10. BottomInfo: Show [Deleted] tag next to timestamp in layoutDateText
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/history/view/history_view_bottom_info.cpp",
        "\tconst auto full = (_data.flags & Data::Flag::Sponsored)\n\t\t? QString()\n\t\t: (_data.flags & Data::Flag::Imported)\n\t\t? (date + ' ' + tr::lng_imported(tr::now))\n\t\t: name.isEmpty()\n\t\t? date\n\t\t: (name + afterAuthor);",
        "\tconst auto deleted = (_data.flags & Data::Flag::Deleted)\n\t\t? u\"[Deleted] \"_q\n\t\t: QString();\n\tconst auto full = (_data.flags & Data::Flag::Sponsored)\n\t\t? QString()\n\t\t: deleted + ((_data.flags & Data::Flag::Imported)\n\t\t? (date + ' ' + tr::lng_imported(tr::now))\n\t\t: name.isEmpty()\n\t\t? date\n\t\t: (name + afterAuthor));"
    )

    # =========================================================================
    # 11. BottomInfo: Click handler on edited tag to toggle original/edited text
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/history/view/history_view_bottom_info.cpp",
        "\tif (inTime) {\n\t\tresult.cursor = CursorState::Date;\n\t}\n\treturn result;\n}",
        "\tif (inTime) {\n\t\tresult.cursor = CursorState::Date;\n\t\tif (_data.flags & Data::Flag::Edited) {\n\t\t\tconst auto item = view->data();\n\t\t\tresult.link = std::make_shared<LambdaClickHandler>([item](ClickContext) {\n\t\t\t\titem->toggleOriginalEditVersion();\n\t\t\t});\n\t\t}\n\t}\n\treturn result;\n}"
    )

    # =========================================================================
    # 12. Main Account: Per-account freeze (pausedForUi)
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/main/main_account.h",
        "\tvoid logOut();",
        "\tvoid logOut();\n\tvoid setPausedForUi(bool paused);\n\t[[nodiscard]] bool pausedForUi() const;"
    )
    patch_file(
        "Telegram/SourceFiles/main/main_account.h",
        "\tbool _loggingOut = false;",
        "\tbool _loggingOut = false;\n\tbool _pausedForUi = false;"
    )
    patch_file(
        "Telegram/SourceFiles/main/main_account.cpp",
        "void Account::logOut() {",
        "void Account::setPausedForUi(bool paused) {\n\t_pausedForUi = paused;\n}\n\nbool Account::pausedForUi() const {\n\treturn _pausedForUi;\n}\n\nvoid Account::logOut() {"
    )

    # =========================================================================
    # 13. Import tData: Recursive copy + Async folder picker (ABOVE Add Account)
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/settings/sections/settings_information.cpp",
        "#include \"settings/sections/settings_information.h\"",
        "#include \"settings/sections/settings_information.h\"\n#include \"core/file_utilities.h\"\n#include \"core/application.h\"\n#include \"ui/toast/toast.h\"\n#include <QDir>\n#include <QFile>\n#include <QDirIterator>"
    )

    patch_file(
        "Telegram/SourceFiles/settings/sections/settings_information.cpp",
        "not_null<Ui::SlideWrap<Ui::SettingsButton>*> AccountsList::setupAdd() {",
        'not_null<Ui::SlideWrap<Ui::SettingsButton>*> AccountsList::setupAdd() {\n'
        '\tauto importTdata = _outer->add(\n'
        '\t\tobject_ptr<Ui::SlideWrap<Ui::SettingsButton>>(\n'
        '\t\t\t_outer.get(),\n'
        '\t\t\tCreateButtonWithIcon(\n'
        '\t\t\t\t_outer.get(),\n'
        '\t\t\t\trpl::single(u"Import tData"_q),\n'
        '\t\t\t\tst::mainMenuAddAccountButton,\n'
        '\t\t\t\t{\n'
        '\t\t\t\t\t&st::settingsIconAdd,\n'
        '\t\t\t\t\tIconType::Round,\n'
        '\t\t\t\t\t&st::windowBgActive\n'
        '\t\t\t\t})))->setDuration(0);\n'
        '\timportTdata->entity()->setClickedCallback([=] {\n'
        '\t\tFileDialog::GetFolder(\n'
        '\t\t\t_outer.get(),\n'
        '\t\t\tu"Select tdata Directory"_q,\n'
        '\t\t\tQString(),\n'
        '\t\t\t[=](QString &&path) {\n'
        '\t\t\t\tif (!path.isEmpty()) {\n'
        '\t\t\t\t\tconst auto target = cWorkingDir() + u"tdata"_q;\n'
        '\t\t\t\t\tQDir().mkpath(target);\n'
        '\t\t\t\t\tQDirIterator it(path, QDir::Files | QDir::Dirs | QDir::NoDotAndDotDot, QDirIterator::Subdirectories);\n'
        '\t\t\t\t\twhile (it.hasNext()) {\n'
        '\t\t\t\t\t\tit.next();\n'
        '\t\t\t\t\t\tconst auto rel = QDir(path).relativeFilePath(it.filePath());\n'
        '\t\t\t\t\t\tconst auto dst = target + \'/\' + rel;\n'
        '\t\t\t\t\t\tif (it.fileInfo().isDir()) {\n'
        '\t\t\t\t\t\t\tQDir().mkpath(dst);\n'
        '\t\t\t\t\t\t} else {\n'
        '\t\t\t\t\t\t\tQDir().mkpath(QFileInfo(dst).path());\n'
        '\t\t\t\t\t\t\tQFile::remove(dst);\n'
        '\t\t\t\t\t\t\tQFile::copy(it.filePath(), dst);\n'
        '\t\t\t\t\t\t}\n'
        '\t\t\t\t\t}\n'
        '\t\t\t\t\tUi::Toast::Show(u"tData Imported! Please restart Telegram."_q);\n'
        '\t\t\t\t}\n'
        '\t\t\t});\n'
        '\t});'
    )

    # =========================================================================
    # 14. Freeze Account in context menu (right-click on account in list)
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/settings/sections/settings_information.cpp",
        "\t\t\tWindow::MenuAddMarkAsReadAllChatsAction(\n\t\t\t\tsession,\n\t\t\t\twindow->uiShow(),\n\t\t\t\taddAction);",
        "\t\t\tWindow::MenuAddMarkAsReadAllChatsAction(\n\t\t\t\tsession,\n\t\t\t\twindow->uiShow(),\n\t\t\t\taddAction);\n\t\t\taddAction(session->account().pausedForUi() ? u\"Unfreeze Account\"_q : u\"Freeze Account\"_q, [=] {\n\t\t\t\tauto &account = session->account();\n\t\t\t\taccount.setPausedForUi(!account.pausedForUi());\n\t\t\t\tUi::Toast::Show(account.pausedForUi() ? u\"Account Frozen\"_q : u\"Account Unfrozen\"_q);\n\t\t\t}, &st::menuIconBlock);"
    )

    # =========================================================================
    # 15. Ghost Mode: Right-click chat -> Open in Ghost Mode (activates + opens chat)
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/window/window_peer_menu.cpp",
        "#include \"boxes/about_box.h\"",
        "#include \"boxes/about_box.h\"\n#include \"core/core_settings.h\"\n#include \"ui/toast/toast.h\""
    )
    patch_file(
        "Telegram/SourceFiles/window/window_peer_menu.cpp",
        "void Filler::fillContextMenuActions() {",
        "void Filler::fillContextMenuActions() {\n\tif (const auto history = _request.key.history()) {\n\t\tconst auto active = history->ghostModeActive();\n\t\tconst auto controller = _controller;\n\t\t_addAction(active ? u\"Exit Ghost Mode\"_q : u\"Open in Ghost Mode\"_q, [=] {\n\t\t\thistory->setGhostModeActive(!active);\n\t\t\tif (!active) {\n\t\t\t\tcontroller->showPeerHistory(history->peer->id);\n\t\t\t}\n\t\t\tUi::Toast::Show(!active ? u\"Ghost Mode Enabled\"_q : u\"Ghost Mode Disabled\"_q);\n\t\t}, &st::menuIconBlock);\n\t}"
    )

    print("All custom UI & core features applied successfully!")

if __name__ == "__main__":
    main()
