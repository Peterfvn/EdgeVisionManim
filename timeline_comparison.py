from manim import *

class TimelineComparison(Scene):
    def construct(self):
        # ── Color palette (matches presentation v2) ──
        self.camera.background_color = "#FAFAF8"

        GREEN = "#1B5E3B"
        CORAL = "#D94F3D"
        GOLD = "#C88A2C"
        GREEN_LIGHT = "#2E8B57"
        DARK = "#1A1A1A"
        MUTED = "#7A7A7A"
        BORDER = "#E0E0DC"
        CORAL_PALE = "#FDF0EE"
        GOLD_PALE = "#FEF7E8"
        GREEN_PALE = "#E8F0EB"

        # ── Title ──
        title = Text(
            "Time to Pathogen Identification",
            font="Georgia",
            font_size=38,
            color=DARK,
            weight=BOLD,
        )
        title.to_edge(UP, buff=0.5)

        accent_bar = Line(
            start=title.get_left() + LEFT * 0.15,
            end=title.get_left() + LEFT * 0.15 + DOWN * 0.5,
            color=GREEN,
            stroke_width=5,
        )
        accent_bar.align_to(title, UP).shift(UP * 0.05)

        self.play(FadeIn(accent_bar, shift=DOWN * 0.1), Write(title), run_time=1)
        self.wait(0.3)

        # ── Time axis ──
        axis_y = -2.2
        axis_start = -5.5
        axis_end = 5.5
        axis_length = axis_end - axis_start

        axis_line = Line(
            start=[axis_start, axis_y, 0],
            end=[axis_end, axis_y, 0],
            color=BORDER,
            stroke_width=2,
        )

        # Hour markers: 0, 12, 24, 48, 72, 96
        hour_marks = [0, 12, 24, 48, 72, 96]
        tick_group = VGroup()
        for h in hour_marks:
            x = axis_start + (h / 96) * axis_length
            tick = Line(
                start=[x, axis_y - 0.08, 0],
                end=[x, axis_y + 0.08, 0],
                color=MUTED,
                stroke_width=1.5,
            )
            label = Text(f"{h}h", font_size=16, color=MUTED)
            label.next_to(tick, DOWN, buff=0.12)
            tick_group.add(tick, label)

        self.play(Create(axis_line), FadeIn(tick_group), run_time=0.8)
        self.wait(0.3)

        # ── Method definitions ──
        methods = [
            {
                "name": "Blood Culture",
                "hours": 72,        # animate to 72h, then show range label
                "range_label": "48–96 hours",
                "note": "~30% positivity rate",
                "color": CORAL,
                "pale": CORAL_PALE,
                "y_offset": 1.0,
            },
            {
                "name": "Cloud mNGS",
                "hours": 48,        # animate to 48h, then show range
                "range_label": "24–72 hours",
                "note": "Cloud transfer + queue",
                "color": GOLD,
                "pale": GOLD_PALE,
                "y_offset": 0.0,
            },
            {
                "name": "Edge Nanopore",
                "hours": 2,
                "range_label": "< 2 hours",
                "note": "Real-time local processing",
                "color": GREEN_LIGHT,
                "pale": GREEN_PALE,
                "y_offset": -1.0,
            },
        ]

        bar_height = 0.45
        label_x = axis_start

        # Build all labels first
        name_labels = []
        for m in methods:
            y = axis_y + 1.5 + m["y_offset"] * 1.3
            name_label = Text(
                m["name"],
                font_size=22,
                color=DARK,
                weight=BOLD,
            )
            name_label.move_to([label_x + 0.8, y + bar_height / 2 + 0.35, 0])
            name_label.align_to([label_x, 0, 0], LEFT)
            name_labels.append(name_label)

        self.play(
            *[FadeIn(nl, shift=RIGHT * 0.2) for nl in name_labels],
            run_time=0.6,
        )
        self.wait(0.3)

        # ── Animate bars growing ──
        # Blood culture and cloud mNGS grow slowly together,
        # then edge nanopore snaps instantly for dramatic contrast

        bars = []
        time_labels = []
        note_labels = []

        for i, m in enumerate(methods):
            y = axis_y + 1.5 + m["y_offset"] * 1.3
            bar_width = (m["hours"] / 96) * axis_length

            # Background track
            track = Rectangle(
                width=axis_length,
                height=bar_height,
                fill_color=m["pale"],
                fill_opacity=0.5,
                stroke_color=BORDER,
                stroke_width=0.5,
            )
            track.move_to([axis_start + axis_length / 2, y, 0])
            self.add(track)

            # Growing bar (starts as zero-width, we'll animate it)
            bar = Rectangle(
                width=0.001,
                height=bar_height,
                fill_color=m["color"],
                fill_opacity=0.7,
                stroke_width=0,
            )
            bar.move_to([axis_start, y, 0])
            bar.align_to([axis_start, 0, 0], LEFT)
            bars.append((bar, bar_width, y, m))

            # Range label (will appear after bar finishes)
            rlabel = Text(
                m["range_label"],
                font_size=18,
                color=WHITE,
                weight=BOLD,
            )
            time_labels.append(rlabel)

            # Note text
            nlabel = Text(
                m["note"],
                font="Georgia",
                font_size=18,
                color=MUTED,
                slant=ITALIC,
            )
            note_labels.append(nlabel)

        # Add all bars
        for bar, _, _, _ in bars:
            self.add(bar)

        # Animate blood culture and cloud mNGS growing together (slow, dramatic)
        def grow_bar(bar_rect, target_width, y_pos):
            """Return animation to grow a bar to target width."""
            target_bar = Rectangle(
                width=target_width,
                height=bar_height,
                fill_color=bar_rect.get_fill_color(),
                fill_opacity=0.7,
                stroke_width=0,
            )
            target_bar.move_to([axis_start + target_width / 2, y_pos, 0])
            return Transform(bar_rect, target_bar)

        # Phase 1: Blood culture and cloud mNGS race (slowly)
        self.play(
            grow_bar(bars[0][0], bars[0][1], bars[0][2]),
            grow_bar(bars[1][0], bars[1][1], bars[1][2]),
            run_time=4,
            rate_func=linear,
        )

        # Add their time labels
        for i in [0, 1]:
            bar_obj = bars[i][0]
            time_labels[i].move_to(bar_obj.get_center())
            # If bar is wide enough, put label inside; otherwise to the right
            note_labels[i].next_to(bar_obj, RIGHT, buff=0.15)

        self.play(
            FadeIn(time_labels[0]),
            FadeIn(time_labels[1]),
            FadeIn(note_labels[0]),
            FadeIn(note_labels[1]),
            run_time=0.5,
        )

        self.wait(0.8)

        # Phase 2: Edge nanopore SNAPS into place — dramatically fast
        self.play(
            grow_bar(bars[2][0], bars[2][1], bars[2][2]),
            run_time=0.15,
            rate_func=rush_into,
        )

        # Flash effect on the edge bar
        flash_rect = Rectangle(
            width=bars[2][1] + 0.1,
            height=bar_height + 0.1,
            stroke_color=GREEN_LIGHT,
            stroke_width=4,
            fill_opacity=0,
        )
        flash_rect.move_to(bars[2][0].get_center())
        self.play(
            FadeIn(flash_rect, scale=1.1),
            run_time=0.2,
        )
        self.play(FadeOut(flash_rect), run_time=0.3)

        # Edge label — place to the right since bar is tiny
        time_labels[2].move_to(bars[2][0].get_center())
        # Bar is very small, so put label to the right instead
        time_labels[2].next_to(bars[2][0], RIGHT, buff=0.15)
        time_labels[2].set_color(GREEN)
        note_labels[2].next_to(time_labels[2], RIGHT, buff=0.15)

        self.play(
            FadeIn(time_labels[2]),
            FadeIn(note_labels[2]),
            run_time=0.4,
        )

        self.wait(1.0)

        # ── Final callout ──
        callout_text = Text(
            "Edge computing: 40× faster than cloud, 50× faster than culture",
            font_size=20,
            color=GREEN,
            weight=BOLD,
        )
        callout_text.to_edge(DOWN, buff=0.55)

        callout_bg = SurroundingRectangle(
            callout_text,
            buff=0.25,
            fill_color=GREEN_PALE,
            fill_opacity=1,
            stroke_color=GREEN_LIGHT,
            stroke_width=1.5,
            corner_radius=0.05,
        )

        self.play(
            FadeIn(callout_bg, shift=UP * 0.15),
            FadeIn(callout_text, shift=UP * 0.15),
            run_time=0.6,
        )

        self.wait(2.5)