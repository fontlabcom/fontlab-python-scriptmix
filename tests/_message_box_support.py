# this_file: tests/_message_box_support.py
"""Stateful Qt message box double; production App ownership helper stays real."""

from typing import Any, ClassVar


def message_box_type(
    warning: Any = lambda *args: None, question: Any = lambda *args: 0
) -> type:
    """Construct a fresh class so callbacks and owned instances remain test-local."""

    class MessageBox:
        Warning, Question, Ok, Yes, No, Cancel = 2, 4, 8, 1, 0, 16
        NoButton, AcceptRole = -2, 0
        instances: ClassVar[list[Any]] = []

        class StandardButtons:
            def __init__(self, value: Any) -> None:
                self.value = value

        def __init__(self, parent: Any) -> None:
            self.parent = parent
            self.flags = 0x1003
            self.events = []
            self.default = None
            self.instances.append(self)

        def setWindowTitle(self, value: Any) -> None:
            self.title = value

        def setText(self, value: Any) -> None:
            self.text = value

        def setIcon(self, value: Any) -> None:
            self.icon = value

        def setStandardButtons(self, value: Any) -> None:
            self._buttons = value

        def setDefaultButton(self, value: Any) -> None:
            self.default = value

        def buttons(self) -> list[int]:
            return [self.Ok] if self._buttons == self.Ok else [self.Yes, self.No]

        def buttonRole(self, button: int) -> int:
            return self.AcceptRole

        def windowFlags(self) -> int:
            return self.flags

        def setWindowFlags(self, value: Any) -> None:
            self.flags = value
            self.events.append("flags")

        def exec(self) -> int:
            assert self.flags == 0x41003, (
                "Preserve type/chrome and add priority before exec"
            )
            self.events.append("exec")
            cls = type(self)
            if self.icon == self.Question:
                self.answer = cls.question(
                    self.parent, self.title, self.text, self._buttons, self.default
                )
            else:
                assert self.icon == self.Warning and self._buttons == self.Ok
                cls.warning(self.parent, self.title, self.text)
                self.answer = self.Ok
            return self.answer

        def clickedButton(self) -> int:
            return self.answer

        def standardButton(self, button: int) -> int:
            return button

        def deleteLater(self) -> None:
            self.events.append("delete")

    MessageBox.warning = staticmethod(warning)
    MessageBox.question = staticmethod(question)
    return MessageBox


def assert_owned_message(kind: type) -> Any:
    """Check actual menu ownership, preserved flags, execution order and deletion."""
    assert kind.instances, "The actual menu route must construct an owned message box"
    box = kind.instances[-1]
    assert box.events == ["flags", "exec", "delete"]
    assert box.flags == 0x41003
    return box
