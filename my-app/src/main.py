import warnings
warnings.filterwarnings("ignore")

from dataclasses import field
from typing import Callable
import asyncio

import flet as ft
import runShorAlgoForEvenNo as r
from collections import Counter
import flet_charts as fch
from pprint import pprint
import time
import requests
from ddgs import DDGS

import pandas as pd
import imagefeatures
from imagefeatures.process import process
from wordhoard import Synonyms

import languagemodels as lm
import time

@ft.control
class WikiPage(ft.Column):

    def init(self):

        self.search_field = ft.TextField(
            label="Search",
            hint_text="Enter a topic...",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
        )

        self.progress_ring = ft.ProgressRing(
            visible=False,
            width=20,
            height=20,
        )

        self.search_button = ft.ElevatedButton(
            "SEARCH",
            icon=ft.Icons.SEARCH,
            on_click=self.start_search,
        )

        self.result_container = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        
        self.controls = [
            ft.Row(
                controls=[
                    self.search_field,
                    self.search_button,
                    self.progress_ring,
                ]
            ),
            self.result_container,
        ]

    def start_search(self, e):

        query = self.search_field.value.strip()

        if not query:
            return

        self.search_button.disabled = True
        self.progress_ring.visible = True

        self.result_container.controls.clear()

        self.update()

        self.page.run_task(self.search_wiki_async, query)

    async def search_wiki_async(self, query):

        try:

            image_url = (
                f"https://image.pollinations.ai/prompt/{query.replace(' ', ',')}"
            )

            wiki_text = await asyncio.to_thread(
                lambda: lm.get_wiki(query.replace(" ", ","))
            )

            card = ft.Card(
                elevation=10,
                content=ft.Container(
                    padding=0,
                    content=ft.Column(
                        spacing=0,
                        controls=[
                            ft.Container(
                                height=300,
                                content=ft.Column(
                                    scroll=ft.ScrollMode.AUTO,
                                    controls=[
                                        ft.Text(
                                            wiki_text,
                                            selectable=True,
                                        )
                                    ],
                                ),
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Image(
                                        src=image_url,
                                        height=100,
                                    )
                                ],
                            ),
                        ],
                    ),
                ),
            )

            self.result_container.controls.append(card)

        except Exception as ex:

            self.result_container.controls.append(
                ft.Text(f"Error: {ex}")
            )

        finally:

            self.progress_ring.visible = False
            self.search_button.disabled = False

            self.update()

@ft.control
class TranslatorPage(ft.Column):

    
    def init(self):

        self.search_field = ft.TextField(
            label="Search",
            hint_text="Enter a topic...",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
        )

        self.result_container = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        self.search_button = ft.ElevatedButton(
            "TRANSLATE",
            icon=ft.Icons.TRANSCRIBE_ROUNDED,
            on_click=self.start_translate,
        )

        self.progress_ring = ft.ProgressRing(
            visible=False,
            width=20,
            height=20,
        )

        self.controls = [
            ft.Row(
                controls=[
                    self.search_field,
                    self.search_button,
                    self.progress_ring,
                ]
            ),
            self.result_container,
        ]

    def start_translate(self, e):

        query = self.search_field.value.strip()

        if not query:
            return

        self.search_button.disabled = True
        self.progress_ring.visible = True

        self.result_container.controls.clear()

        self.update()

        self.page.run_task(
            self.translate_async,
            query,
        )

    async def translate_async(self, query):

        try:

            translator_text = await asyncio.to_thread(
                lambda: lm.do(
                    f"Translate to English: {query}"
                )
            )

            card = ft.Card(
                elevation=10,
                content=ft.Container(
                    padding=0,
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                height=100,
                                width=300,
                                content=ft.Column(
                                    scroll=ft.ScrollMode.AUTO,
                                    controls=[
                                        ft.Text(
                                            translator_text,
                                            selectable=True,
                                        )
                                    ],
                                ),
                            )
                        ],
                    ),
                ),
            )

            self.result_container.controls.append(card)

        except Exception as ex:

            self.result_container.controls.append(
                ft.Text(f"Error: {ex}")
            )

        finally:

            self.progress_ring.visible = False
            self.search_button.disabled = False

            self.update()

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
class GalleryPage(ft.Column):

    def init(self):
        self.session = requests.Session()

        self.expand = True
        self.spacing = 10

        self.feature_cache = {}

        self.search_field = ft.TextField(
            hint_text="Search images...",
            expand=True,
            on_submit=self.search_images,
        )

        self.search_button = ft.Button(
            "Search",
            on_click=self.search_images,
        )

        self.status_text = ft.Text("")

        # Horizontal scrolling gallery
        self.gallery = ft.Row(
            expand=True,
            wrap=False,
            scroll=ft.ScrollMode.ALWAYS,
            spacing=10,
        )

        self.feature_text = ft.Text(
            "Click on an image to generate features",
            selectable=True,
        )

        self.embedding_chart = fch.LineChart(data_series=[], expand=True, height=300)

        self.feature_panel = ft.Container(
            padding=15,
            border_radius=10,
            content=ft.Column(
                [
                    ft.Text(
                        "Image Features",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                    self.feature_text,
                    self.embedding_chart,
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
        )

        self.controls = [
            ft.Row(
                [
                    self.search_field,
                    self.search_button,
                ]
            ),
            self.status_text,
            ft.Container(
                height=220,
                content=self.gallery,
            ),
            self.feature_panel,
        ]


    def update_embedding_chart(self, result_dict):

        embedding_cols = sorted(
            [
                c
                for c in result_dict.keys()
                if c.startswith("image_url_embedding_")
            ],
            key=lambda x: int(x.split("_")[-1])
        )

        values = [
            float(result_dict[c])
            for c in embedding_cols
        ]

        points = [
            fch.LineChartDataPoint(i, value)
            for i, value in enumerate(values)
        ]

        self.embedding_chart.data_series = [
            fch.LineChartData(
                points=points,
                curved=True,
                stroke_width=2,
            )
        ]

    def search_images(self, e):
        query = self.search_field.value.strip()

        if not query:
            self.status_text.value = "Please enter a search query."
            self.update()
            return

        self.status_text.value = f"Searching for '{query}'..."
        self.gallery.controls.clear()
        self.update()

        try:
            with DDGS() as ddgs:
                results = list(
                    ddgs.images(
                        query=query,
                        max_results=30,
                    )
                )

            if not results:
                self.status_text.value = "No images found."
                self.update()
                return

            for item in results:

                image_url = item.get("image")

                if not image_url:
                    continue

                self.gallery.controls.append(
                    ft.Container(
                        width=200,
                        height=200,
                        border_radius=10,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=ft.Image(
                            src=image_url,
                            width=200,
                            height=200,
                            fit=ft.BoxFit.COVER,
                            border_radius=ft.BorderRadius.all(10),
                        ),
                        on_click=lambda e, url=image_url: self.show_features(
                            e, url
                        ),
                    )
                )

            self.status_text.value = (
                f"Found {len(self.gallery.controls)} images."
            )

        except Exception as ex:
            self.status_text.value = f"Search Error: {ex}"

        self.update()

    def show_features(self, e, image_url):

        if e.data == "false":
            return

        try:

            if image_url in self.feature_cache:
                self.feature_text.value = self.feature_cache[image_url]
                self.update()
                return

            self.feature_text.value = "Generating features..."
            self.update()

            df = pd.DataFrame(
                {
                    "image_url": [image_url]
                }
            )

            result = process(
                df,
                {"image_url"},
                self.session,
            )

            result_dict = (
                result.copy()
                .to_dict(orient="records")[0]
            )

            self.update_embedding_chart(result_dict)
            features = []

            for feat in [
                "image_url_average_blue",
                "image_url_average_green",
                "image_url_average_red",
                "image_url_luminosity",
            ]:

                if feat in result_dict:
                    features.append(
                        f"{feat[10:].replace('_', '-').upper()}: {result_dict[feat]}"
                    )

            features_text = " <=> ".join(features)

            self.feature_cache[image_url] = features_text

            self.feature_text.value = features_text

        except Exception as ex:
            self.feature_text.value = (
                f"Feature Extraction Error:\n{ex}"
            )

        self.update()



@ft.control
class SynonymPage(ft.Column):

    def init(self):
        self.search_field = ft.TextField(
            hint_text="Search for synonyms...",
            expand=True,
            on_submit=self.start_search,
        )

        self.search_button = ft.ElevatedButton(
            "Search",
            on_click=self.start_search,
        )

        self.progress_ring = ft.ProgressRing(
            visible=False,
            width=20,
            height=20,
        )

        self.status_text = ft.Text()

        self.tasks = ft.Column(
            wrap=True,
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
        )

        self.controls = [
            ft.Row(
                [
                    self.search_field,
                    self.search_button,
                    self.progress_ring,
                ]
            ),
            self.status_text,
            ft.Container(
                height=220,
                content=self.tasks,
            ),
        ]

    def start_search(self, e):
        """
        Called immediately from button click.
        Shows progress ring and launches background task.
        """

        query = self.search_field.value.strip()

        if not query:
            self.status_text.value = "Please enter a word."
            self.update()
            return

        if len(query.split()) > 1:
            self.status_text.value = "Please enter a single word."
            self.update()
            return

        self.search_button.disabled = True
        self.progress_ring.visible = True
        self.status_text.value = f"Searching for direction, beauty and meaning of '{query}'..."
        self.tasks.controls.clear()

        self.update()

        # same pattern as Analytics/ToDo pages
        self.page.run_task(self.search_synonyms_async, query)

    async def search_synonyms_async(self, query):

        try:

            # move blocking work to thread
            synonyms_results = await asyncio.to_thread(
                lambda: Synonyms(query).find_synonyms()
            )

            synonyms = (
                synonyms_results
                if synonyms_results
                else ["No synonyms found"]
            )

            controls = []

            def fetch_images():
                results = []

                with DDGS() as ddgs:
                    for word in synonyms:

                        image_results = list(
                            ddgs.images(
                                query=word,
                                max_results=1,
                            )
                        )

                        image_url = ""

                        if image_results:
                            image_url = image_results[0].get("image", "")

                        results.append((word, image_url))

                return results

            image_data = await asyncio.to_thread(fetch_images)

            for word, image_url in image_data:

                controls.append(
                    ft.Container(
                        width=200,
                        height=200,
                        border_radius=10,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=ft.Image(
                            src=image_url,
                            fit=ft.BoxFit.COVER,
                        ),
                    )
                )

                controls.append(
                    ft.Container(
                        ft.Text(f"{word}"),
                        width=100,
                        height=100,
                        alignment=ft.Alignment.CENTER,
                        bgcolor=ft.Colors.AMBER_100,
                        border=ft.Border.all(1, ft.Colors.AMBER_400),
                        border_radius=ft.BorderRadius.all(5),
                    )
                )

            self.tasks.controls = controls

            self.status_text.value = (
                f"Found {len(synonyms)} synonym(s)"
            )

        except Exception as ex:

            self.status_text.value = f"Error: {ex}"

        finally:

            self.progress_ring.visible = False
            self.search_button.disabled = False

            self.update()

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
        self.gallery_page = GalleryPage()
        self.synonym_page = SynonymPage()
        self.wiki_page = WikiPage()
        self.translator_page = TranslatorPage()

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
                ft.NavigationBarDestination(
                    icon=ft.Icons.BROWSE_GALLERY_SHARP,
                    label="ImageGallery",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.SYNAGOGUE_ROUNDED,
                    label="SynonymGenerator",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.WIDGETS,
                    label="Wiki",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.TRANSCRIBE,
                    label="Translator",
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

        elif e.control.selected_index == 1:
            self.page_body.content = self.analytics_page
        
        elif e.control.selected_index == 2:
            self.page_body.content = self.gallery_page
        
        elif e.control.selected_index == 3:
            self.page_body.content = self.synonym_page
        
        elif e.control.selected_index == 4:
            self.page_body.content = self.wiki_page

        elif e.control.selected_index == 5:
            self.page_body.content = self.translator_page


        self.update()

def main(page: ft.Page):
    page.title = "modernWebApp"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.width = 500
    page.window.height = 600
    page.add(MultiPageApp())


if __name__ == "__main__":
    ft.run(main)
