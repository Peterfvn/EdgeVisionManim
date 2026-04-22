from manim import *

class CompressionCascade(Scene):
    def construct(self):
        self.camera.background_color = "#FAFAF8"

        # ── Colors ──
        GREEN = "#1B5E3B"
        CORAL = "#D94F3D"
        GOLD = "#C88A2C"
        GREEN_LIGHT = "#2E8B57"
        DARK = "#1A1A1A"
        MUTED = "#6B6B6B"
        LIGHT_MUTED = "#999999"
        BORDER = "#E0E0DC"
        GREEN_PALE = "#E8F0EB"

        FONT = "Georgia"

        # ── Title ──
        title = Text(
            "The Compression Cascade",
            font=FONT,
            font_size=40,
            color=DARK,
            weight=BOLD,
        )
        title.to_edge(UP, buff=0.45)

        accent_bar = Line(
            start=title.get_left() + LEFT * 0.2,
            end=title.get_left() + LEFT * 0.2 + DOWN * 0.55,
            color=GREEN,
            stroke_width=5,
        )
        accent_bar.align_to(title, UP).shift(UP * 0.05)

        self.play(
            FadeIn(accent_bar, shift=DOWN * 0.1),
            Write(title),
            run_time=0.8,
        )
        self.wait(0.3)

        # ── Stage data ──
        stages = [
            {
                "label": "Raw Signal",
                "size": "~30 GB",
                "process": "MinION electrical output",
                "width": 11.0,
                "color": CORAL,
            },
            {
                "label": "Basecalled Reads",
                "size": "~3 GB",
                "process": "Dorado (GPU)",
                "width": 7.5,
                "color": GOLD,
                "reduction": "10×",
            },
            {
                "label": "Microbial Reads",
                "size": "~30 MB",
                "process": "Bowtie2 filtering",
                "width": 3.5,
                "color": GREEN_LIGHT,
                "reduction": "100×",
            },
            {
                "label": "Pathogen Report",
                "size": "~KB",
                "process": "Kraken2 classification",
                "width": 1.0,
                "color": GREEN,
                "reduction": "1,000×",
            },
        ]

        bar_height = 0.65
        gap = 0.55          # vertical gap between bars
        top_y = 1.8        # y-center of the first bar

        # ── Build each row: bar + labels, animate sequentially ──
        prev_bar = None

        for i, stage in enumerate(stages):
            y = top_y - i * (bar_height + gap)

            # The bar itself
            bar = Rectangle(
                width=stage["width"],
                height=bar_height,
                fill_color=stage["color"],
                fill_opacity=0.75,
                stroke_width=0,
            )
            bar.move_to([0, y, 0])

            # Size label (right-aligned outside bar, or inside if bar is big)
            size_label = Text(
                stage["size"],
                font=FONT,
                font_size=22,
                color=DARK,
                weight=BOLD,
            )

            # Stage name (left-aligned inside bar for wide bars, or next to it)
            name_label = Text(
                stage["label"],
                font=FONT,
                font_size=20,
                color=WHITE,
                weight=BOLD,
            )

            # Process note (below bar, small italic)
            process_label = Text(
                stage["process"],
                font=FONT,
                font_size=16,
                color=LIGHT_MUTED,
                slant=ITALIC,
            )

            if stage["width"] >= 5:
                # Wide bar: labels inside
                name_label.move_to(bar.get_center() + LEFT * (stage["width"] / 2 - 1.2))
                name_label.align_to(bar, LEFT).shift(RIGHT * 0.3)
                size_label.move_to(bar.get_center() + RIGHT * (stage["width"] / 2 - 0.8))
                size_label.align_to(bar, RIGHT).shift(LEFT * 0.3)
                size_label.set_color(WHITE)
            elif stage["width"] >= 2:
                # Medium bar: name inside, size to the right
                name_label.move_to(bar.get_center())
                size_label.next_to(bar, RIGHT, buff=0.25)
            else:
                # Tiny bar: both labels to the right
                name_label.next_to(bar, RIGHT, buff=0.2)
                name_label.set_color(DARK)
                size_label.next_to(name_label, RIGHT, buff=0.2)

            process_label.next_to(bar, DOWN, buff=0.06)
            process_label.align_to(bar, LEFT)
            # For very small bars, align to bar left but don't go off screen
            if stage["width"] < 3:
                process_label.move_to([0, y - bar_height / 2 - 0.18, 0])

            # ── Animate this row ──
            if i == 0:
                # First bar: grow from left
                self.play(GrowFromEdge(bar, LEFT), run_time=0.8)
                self.play(
                    FadeIn(name_label),
                    FadeIn(size_label),
                    FadeIn(process_label, shift=UP * 0.05),
                    run_time=0.4,
                )
            else:
                # Subsequent bars: show reduction label, then reveal bar

                # Reduction arrow + label between previous bar and this one
                reduction_text = Text(
                    stage["reduction"],
                    font=FONT,
                    font_size=28,
                    color=stage["color"],
                    weight=BOLD,
                )
                arrow_y = y + (bar_height + gap) / 2
                reduction_text.move_to([4.5, arrow_y, 0])

                down_arrow = Text(
                    "↓",
                    font_size=24,
                    color=LIGHT_MUTED,
                )
                down_arrow.next_to(reduction_text, LEFT, buff=0.2)

                self.play(
                    FadeIn(reduction_text, shift=DOWN * 0.1),
                    FadeIn(down_arrow, shift=DOWN * 0.1),
                    run_time=0.35,
                )
                self.play(GrowFromEdge(bar, LEFT), run_time=0.6)
                self.play(
                    FadeIn(name_label),
                    FadeIn(size_label),
                    FadeIn(process_label, shift=UP * 0.05),
                    run_time=0.35,
                )

            prev_bar = bar
            self.wait(0.5)

        self.wait(0.5)

        # ── Final callout ──
        callout_text = Text(
            "30 GB in, kilobytes out. No data leaves the hospital's network",
            font=FONT,
            font_size=22,
            color=GREEN,
            weight=BOLD,
        )
        callout_text.to_edge(DOWN, buff=0.35)

        callout_bg = SurroundingRectangle(
            callout_text,
            buff=0.2,
            fill_color=GREEN_PALE,
            fill_opacity=1,
            stroke_color=GREEN_LIGHT,
            stroke_width=1.5,
            corner_radius=0.05,
        )

        self.play(
            FadeIn(callout_bg, shift=UP * 0.1),
            FadeIn(callout_text, shift=UP * 0.1),
            run_time=0.5,
        )

        self.wait(2.5)