from dataclasses import field
from typing import Callable

import flet as ft
import runShorAlgoForEvenNo as r


@ft.control
class Task(ft.Column):
    task_name: str = ""
    on_status_change: Callable[[], None] = field(default=lambda: None)
    on_delete: Callable[["Task"], None] = field(default=lambda task: None)

    def init(self):
        self.completed = False

        self.display_task = ft.Checkbox(
            value=False,
            label=self.task_name,
            on_change=self.status_changed,
        )

        self.edit_name = ft.TextField(
            expand=1,
            input_filter=ft.NumbersOnlyInputFilter(),
        )

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CREATE_OUTLINED,
                            tooltip="Edit",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            tooltip="Delete",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.Icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.Colors.GREEN,
                    tooltip="Update",
                    on_click=self.save_clicked,
                ),
            ],
        )

        self.controls = [self.display_view, self.edit_view]

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def status_changed(self, e):
        self.completed = self.display_task.value
        self.on_status_change()

    def delete_clicked(self, e):
        self.on_delete(self)


@ft.control
class TodoApp(ft.Column):

    def init(self):
        self.new_task = ft.TextField(
            hint_text="Enter an integer",
            expand=True,
            input_filter=ft.NumbersOnlyInputFilter(),
        )

        self.tasks = ft.ListView(
            expand=True,
            spacing=5,
            auto_scroll=True,
        )

        self.filter = ft.TabBar(
            scrollable=False,
            tabs=[
                ft.Tab(label="all"),
                ft.Tab(label="active"),
                ft.Tab(label="completed"),
            ],
        )

        self.filter_tabs = ft.Tabs(
            length=3,
            selected_index=0,
            on_change=lambda e: self.update(),
            content=self.filter,
        )

        self.width = 900

        self.controls = [
            ft.Row(
                controls=[
                    self.new_task,
                    ft.FloatingActionButton(
                        icon=ft.Icons.ADD,
                        on_click=self.add_clicked,
                    ),
                ],
            ),
            ft.Column(
                spacing=25,
                controls=[
                    self.filter_tabs,
                    self.tasks,
                ],
            ),
        ]

    def add_clicked(self, e):
        if not self.new_task.value:
            return

        number = self.new_task.value

        task = Task(
            task_name=f"Computing prime factors for {number}...",
            on_status_change=self.task_status_change,
            on_delete=self.task_delete,
        )

        self.tasks.controls.append(task)

        self.new_task.value = ""
        self.update()

        self.page.run_thread(
            self.compute_factorization,
            task,
            int(number),
        )

    def compute_factorization(self, task, number):
        try:
            if len(str(number)) >= 100:
                result = (
                    f"Prime Factorization for {number} is going to be very slow. "
                    f"Please try a smaller integer."
                )
            else:
                factors = r.parallel_for_loop_factor(number)
                result = f"Prime Factorization for {number}: {factors}"

            task.display_task.label = result

        except Exception as ex:
            task.display_task.label = f"Error: {str(ex)}"

        task.update()

    def task_status_change(self):
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()

    def before_update(self):
        status = self.filter.tabs[self.filter_tabs.selected_index].label

        for task in self.tasks.controls:
            task.visible = (
                status == "all"
                or (status == "active" and not task.completed)
                or (status == "completed" and task.completed)
            )

    def tabs_changed(self, e):
        self.update()


def main(page: ft.Page):
    page.title = (
        "Integer Prime Factorization Shor Algorithm App"
    )

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    app = TodoApp()

    page.add(app)


if __name__ == "__main__":
    ft.run(main)