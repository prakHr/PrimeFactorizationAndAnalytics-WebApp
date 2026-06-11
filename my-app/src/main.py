from dataclasses import field
from typing import Callable

import flet as ft
import runShorAlgoForEvenNo as r
from collections import Counter
import flet_charts as fch

import time

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


@ft.control
class AnalyticsPage(ft.Column):
    def create_shimmer(self):
        accent = ft.LinearGradient(
            begin=ft.Alignment(-1.0, -0.5),
            end=ft.Alignment(1.0, 0.5),
            colors=[
                ft.Colors.WHITE,
                ft.Colors.BLUE,
                ft.Colors.WHITE,
                ft.Colors.WHITE,
                ft.Colors.BLUE,
            ],
            stops=[0.0, 0.35, 0.5, 0.65, 1.0],
        )

        return ft.Container(
            expand=True,
            alignment=ft.Alignment(0, 0),
            content=ft.Shimmer(
                gradient=accent,
                direction=ft.ShimmerDirection.LTR,
                period=1800,
                content=ft.Container(
                    width=300,
                    height=300,
                    border_radius=150,
                    bgcolor=ft.Colors.with_opacity(
                        0.3,
                        ft.Colors.WHITE,
                    ),
                ),
            ),
        )
    def init(self):

        self.input_numbers = ft.TextField(
            label="Comma separated integers",
            hint_text="10,20,30,40",
        )

        self.chart_container = ft.Container()

        self.controls = [
            ft.Text(
                "Create Pie Chart - Analytics Dashboard",
                size=24,
                weight=ft.FontWeight.BOLD,
            ),
            self.input_numbers,
           ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Button(
                        "Generate Pie Chart",
                        on_click=self.generate_chart,
                    ),
                    ft.Button(
                        "Generate Line Chart",
                        on_click=self.generate_line_chart,
                    ),
                ],
            ),
            self.chart_container,
        ]

    def build_line_chart(self):

        time.sleep(0.25)

        try:

            values = [
                int(x.strip())
                for x in self.input_numbers.value.split(",")
                if x.strip()
            ]

            if not values:
                return

            points = [
                fch.LineChartDataPoint(i, value)
                for i, value in enumerate(values)
            ]

            data_series = [
                fch.LineChartData(
                    stroke_width=4,
                    color=ft.Colors.BLUE,
                    curved=True,
                    rounded_stroke_cap=True,
                    points=points,
                )
            ]

            chart = fch.LineChart(
                expand=True,
                data_series=data_series,

                min_x=0,
                max_x=max(len(values) - 1, 1),

                min_y=0,
                max_y=max(values) + 5,

                border=ft.Border.all(
                    1,
                    ft.Colors.with_opacity(
                        0.2,
                        ft.Colors.ON_SURFACE,
                    ),
                ),

                horizontal_grid_lines=fch.ChartGridLines(
                    interval=max(
                        1,
                        max(values) // 5,
                    ),
                    color=ft.Colors.with_opacity(
                        0.2,
                        ft.Colors.ON_SURFACE,
                    ),
                    width=1,
                ),

                vertical_grid_lines=fch.ChartGridLines(
                    interval=1,
                    color=ft.Colors.with_opacity(
                        0.2,
                        ft.Colors.ON_SURFACE,
                    ),
                    width=1,
                ),

                tooltip=fch.LineChartTooltip(
                    bgcolor=ft.Colors.with_opacity(
                        0.8,
                        ft.Colors.BLUE_GREY,
                    ),
                ),

                left_axis=fch.ChartAxis(
                    label_size=40,
                ),

                bottom_axis=fch.ChartAxis(
                    label_size=40,
                    labels=[
                        fch.ChartAxisLabel(
                            value=i,
                            label=ft.Text(str(i + 1)),
                        )
                        for i in range(len(values))
                    ],
                ),
            )

            self.chart_container.content = chart
            self.update()

        except Exception as ex:
            pass

    def generate_line_chart(self, e):

        self.chart_container.content = self.create_shimmer()

        self.update()

        self.page.run_thread(self.build_line_chart)

    def generate_chart(self, e):

        self.chart_container.content = self.create_shimmer()
        
        self.update()
        self.page.run_thread(self.build_chart)

    def build_chart(self):
        time.sleep(0.25)  # Simulate data processing delay
        try:
            values = [
                int(x.strip())
                for x in self.input_numbers.value.split(",")
                if x.strip()
            ]

            colors = [
                ft.Colors.BLUE,
                ft.Colors.RED,
                ft.Colors.GREEN,
                ft.Colors.ORANGE,
                ft.Colors.PURPLE,
                ft.Colors.CYAN,
            ]
            counts = Counter(values)
            total = sum(counts.values())
            sections = []
            for i, (number, count) in enumerate(counts.items()):

                percentage = round((count / total) * 100, 2)

                sections.append(
                    fch.PieChartSection(
                        value=count,
                        title=f"{number} ({percentage}%)",
                        color=colors[i % len(colors)],
                        radius=100,
                    )
                )
            chart = fch.PieChart(
                sections=sections,
                expand=True,
            )

            self.chart_container.content = chart
            self.update()

        except Exception as ex:
            pass



@ft.control
class MultiPageApp(ft.Column):

    def theme_changed(self, e):

        if e.control.value:
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT

        self.page.update()

    def init(self):

        self.todo_page = TodoApp()
        self.analytics_page = AnalyticsPage()

        self.page_body = ft.Container(
            content=self.todo_page,
            expand=True,
        )

        self.navbar = ft.CupertinoNavigationBar(
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.CHECKLIST,
                    label="ToCalcPrimeFactors",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.ANALYTICS,
                    label="Analytics",
                ),
            ],
            on_change=self.nav_changed,
        )

        self.theme_switch = ft.Switch(
            label="Dark Mode",
            value=False,
            on_change=self.theme_changed,
        )

        self.controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    self.theme_switch,
                ],
            ),
            self.page_body,
        ]


    def did_mount(self):
        self.page.navigation_bar = self.navbar
        self.page.update()

    def nav_changed(self, e):

        if e.control.selected_index == 0:
            self.page_body.content = self.todo_page

        else:
            self.page_body.content = self.analytics_page

        self.update()

def main(page: ft.Page):
    page.title = "modernWebApp"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(MultiPageApp())


if __name__ == "__main__":
    ft.run(main)
