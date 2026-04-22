from manim import *

class ArchitectureFlow(Scene):
    def construct(self):
        self.camera.background_color = "#FAFAF8"

        # ── Colors ──
        GREEN = "#1B5E3B"
        CORAL = "#D94F3D"
        GOLD = "#C88A2C"
        GREEN_LIGHT = "#2E8B57"
        DARK = "#1A1A1A"
        MUTED = "#6B6B6B"
        LIGHT_MUTED = "#AAAAAA"
        BORDER = "#D0D0CC"
        GREEN_PALE = "#E8F0EB"
        CORAL_PALE = "#FDF0EE"
        GOLD_PALE = "#FEF7E8"
        NAVY = "#1C2D41"

        FONT = "Georgia"

        # ── Title ──
        title = Text(
            "System Architecture",
            font=FONT,
            font_size=40,
            color=DARK,
            weight=BOLD,
        )
        title.to_edge(UP, buff=0.4)

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

        # ════════════════════════════════════════
        # LAYOUT — left to right flow
        # ════════════════════════════════════════
        #
        # [Blood Sample] → [MinION] → [ EDGE NODE ─────────────── ]  → [Report]
        #                               │ Basecalling              │
        #                               │ Filtering                │
        #                               │ Classification           │
        #                               │ AMR Detection            │
        #                              [─────────────────────────── ]
        #                                        ╎ async
        #                                   [Cloud Backend]

        row_y = 0.5  # vertical center of the main flow

        # ── Blood Sample box ──
        sample_box = Rectangle(
            width=1.6, height=0.9,
            fill_color=CORAL_PALE, fill_opacity=1,
            stroke_color=CORAL, stroke_width=1.5,
        )
        sample_box.move_to([-5.5, row_y, 0])

        sample_label = Text("Blood\nSample", font=FONT, font_size=16, color=DARK, weight=BOLD)
        sample_label.move_to(sample_box.get_center())

        # ── MinION box ──
        minion_box = Rectangle(
            width=1.6, height=0.9,
            fill_color=GOLD_PALE, fill_opacity=1,
            stroke_color=GOLD, stroke_width=1.5,
        )
        minion_box.move_to([-3.2, row_y, 0])

        minion_label = Text("MinION", font=FONT, font_size=16, color=DARK, weight=BOLD)
        minion_sub = Text("USB-C", font=FONT, font_size=12, color=MUTED)
        minion_labels = VGroup(minion_label, minion_sub).arrange(DOWN, buff=0.08)
        minion_labels.move_to(minion_box.get_center())

        # ── Arrow: sample → minion ──
        arrow1 = Arrow(
            sample_box.get_right(), minion_box.get_left(),
            buff=0.1, color=MUTED, stroke_width=2,
            max_tip_length_to_length_ratio=0.2,
        )

        # ── Edge Node container ──
        edge_box_solid = Rectangle(
            width=5.2, height=3.2,
            fill_color=WHITE, fill_opacity=0.5,
            stroke_color=GREEN, stroke_width=2,
        )
        edge_box_solid.move_to([1.8, row_y - 0.4, 0])
        edge_box = DashedVMobject(edge_box_solid, num_dashes=40)
        # Keep a reference rectangle for positioning
        edge_ref = edge_box_solid

        edge_title = Text(
            "EDGE NODE — Jetson Thor",
            font=FONT, font_size=15, color=GREEN, weight=BOLD,
        )
        edge_title.next_to(edge_ref, UP, buff=0.08)

        # ── Arrow: minion → edge ──
        arrow2 = Arrow(
            minion_box.get_right(), edge_ref.get_left() + UP * 0.8,
            buff=0.1, color=GREEN, stroke_width=2,
            max_tip_length_to_length_ratio=0.15,
        )

        # ── Pipeline stages inside edge node ──
        stage_data = [
            {"label": "Basecalling (Dorado)", "detail": "GPU", "color": CORAL},
            {"label": "Human Read Filtering", "detail": "CPU", "color": GOLD},
            {"label": "Classification (Kraken2)", "detail": "CPU", "color": GREEN_LIGHT},
            {"label": "AMR Detection", "detail": "parallel", "color": GREEN},
        ]

        stage_width = 4.4
        stage_height = 0.5
        stage_gap = 0.18
        stages_top = edge_ref.get_top()[1] - 0.55

        stage_boxes = []
        stage_labels_group = []

        for j, sd in enumerate(stage_data):
            sy = stages_top - j * (stage_height + stage_gap)
            sbox = Rectangle(
                width=stage_width, height=stage_height,
                fill_color=sd["color"], fill_opacity=0.15,
                stroke_color=sd["color"], stroke_width=1,
            )
            sbox.move_to([edge_ref.get_center()[0], sy, 0])

            slabel = Text(sd["label"], font=FONT, font_size=14, color=DARK, weight=BOLD)
            slabel.move_to(sbox.get_center() + LEFT * 0.8)
            slabel.align_to(sbox, LEFT).shift(RIGHT * 0.2)

            sdetail = Text(sd["detail"], font=FONT, font_size=12, color=MUTED, slant=ITALIC)
            sdetail.align_to(sbox, RIGHT).shift(LEFT * 0.25)
            sdetail.set_y(sbox.get_center()[1])

            stage_boxes.append(sbox)
            stage_labels_group.append(VGroup(slabel, sdetail))

        # Down arrows between stages
        stage_arrows = []
        for j in range(len(stage_boxes) - 1):
            sa = Arrow(
                stage_boxes[j].get_bottom(),
                stage_boxes[j + 1].get_top(),
                buff=0.04, color=LIGHT_MUTED, stroke_width=1.5,
                max_tip_length_to_length_ratio=0.35,
            )
            stage_arrows.append(sa)

        # ── Report output ──
        report_box = Rectangle(
            width=1.8, height=0.7,
            fill_color=GREEN_PALE, fill_opacity=1,
            stroke_color=GREEN_LIGHT, stroke_width=1.5,
        )
        report_box.move_to([5.8, row_y - 0.4, 0])

        report_label = Text("Pathogen\nReport", font=FONT, font_size=15, color=GREEN, weight=BOLD)
        report_label.move_to(report_box.get_center())

        report_sub = Text("→ EMR", font=FONT, font_size=12, color=MUTED)
        report_sub.next_to(report_box, DOWN, buff=0.1)

        # Arrow: edge → report
        arrow3 = Arrow(
            edge_ref.get_right() + DOWN * 0.4,
            report_box.get_left(),
            buff=0.1, color=GREEN_LIGHT, stroke_width=2,
            max_tip_length_to_length_ratio=0.2,
        )

        # ── Cloud Backend (below) ──
        cloud_box_solid = Rectangle(
            width=2.8, height=0.9,
            fill_color=WHITE, fill_opacity=0.8,
            stroke_color=BORDER, stroke_width=1.5,
        )
        cloud_box_solid.move_to([edge_ref.get_center()[0], -2.8, 0])
        cloud_box = DashedVMobject(cloud_box_solid, num_dashes=20)
        cloud_ref = cloud_box_solid

        cloud_label = Text("Cloud Backend", font=FONT, font_size=15, color=MUTED, weight=BOLD)
        cloud_sub = Text("surveillance · DB updates · archival", font=FONT, font_size=11, color=LIGHT_MUTED)
        cloud_labels = VGroup(cloud_label, cloud_sub).arrange(DOWN, buff=0.06)
        cloud_labels.move_to(cloud_ref.get_center())

        # Dashed line: edge ↔ cloud
        cloud_line = DashedLine(
            edge_ref.get_bottom(),
            cloud_ref.get_top(),
            dash_length=0.12,
            color=LIGHT_MUTED,
            stroke_width=1.5,
        )
        async_label = Text("async", font=FONT, font_size=11, color=LIGHT_MUTED, slant=ITALIC)
        async_label.next_to(cloud_line, RIGHT, buff=0.12)

        # ════════════════════════════════════════
        # ANIMATION SEQUENCE
        # ════════════════════════════════════════

        # Phase 1: Build the static architecture (fast)
        self.play(
            FadeIn(sample_box), FadeIn(sample_label),
            run_time=0.4,
        )
        self.play(
            GrowArrow(arrow1),
            FadeIn(minion_box), FadeIn(minion_labels),
            run_time=0.5,
        )
        self.play(
            GrowArrow(arrow2),
            FadeIn(edge_box), FadeIn(edge_title),
            run_time=0.5,
        )

        # Stages appear one by one
        for j in range(len(stage_boxes)):
            anims = [FadeIn(stage_boxes[j]), FadeIn(stage_labels_group[j])]
            if j > 0:
                anims.append(GrowArrow(stage_arrows[j - 1]))
            self.play(*anims, run_time=0.3)

        # Output + cloud
        self.play(
            GrowArrow(arrow3),
            FadeIn(report_box), FadeIn(report_label), FadeIn(report_sub),
            run_time=0.4,
        )
        self.play(
            Create(cloud_line), FadeIn(async_label),
            FadeIn(cloud_box), FadeIn(cloud_labels),
            run_time=0.5,
        )

        self.wait(0.5)

        # Phase 2: Animate data flowing through the pipeline
        # A colored dot travels from sample → minion → through each stage → report
        # It shrinks and changes color at each stage (no size labels — the
        # compression cascade animation already covered that)

        dot_radius = 0.15
        data_dot = Circle(
            radius=dot_radius,
            fill_color=CORAL,
            fill_opacity=0.9,
            stroke_width=0,
        )
        data_dot.move_to(sample_box.get_center())

        self.play(FadeIn(data_dot, scale=0.5), run_time=0.5)
        self.wait(0.3)

        # Move to MinION
        self.play(
            data_dot.animate.move_to(minion_box.get_center()),
            run_time=0.8,
        )
        self.wait(0.3)

        # Move into edge node, first stage
        self.play(
            data_dot.animate.move_to(stage_boxes[0].get_center()),
            stage_boxes[0].animate.set_fill(opacity=0.35),
            run_time=0.8,
        )
        self.wait(0.5)

        # Flow through remaining stages with shrinking + color change
        flow_data = [
            {"color": GOLD, "radius": 0.11},
            {"color": GREEN_LIGHT, "radius": 0.07},
            {"color": GREEN, "radius": 0.04},
        ]

        for j, fd in enumerate(flow_data):
            target_stage = stage_boxes[j + 1]

            new_dot = Circle(
                radius=fd["radius"],
                fill_color=fd["color"],
                fill_opacity=0.9,
                stroke_width=0,
            )
            new_dot.move_to(target_stage.get_center())

            self.play(
                Transform(data_dot, new_dot),
                target_stage.animate.set_fill(opacity=0.35),
                run_time=0.7,
            )
            self.wait(0.4)

        # Data dot exits to report
        final_dot = Circle(
            radius=0.04,
            fill_color=GREEN,
            fill_opacity=0.9,
            stroke_width=0,
        )
        final_dot.move_to(report_box.get_center())

        self.play(
            Transform(data_dot, final_dot),
            run_time=0.6,
        )

        # Flash the report box
        report_flash = SurroundingRectangle(
            report_box, buff=0.08,
            stroke_color=GREEN_LIGHT, stroke_width=3,
            fill_opacity=0,
        )
        self.play(FadeIn(report_flash, scale=1.05), run_time=0.3)
        self.play(FadeOut(report_flash), FadeOut(data_dot), run_time=0.4)

        # Reset stage highlights
        self.play(
            *[sb.animate.set_fill(opacity=0.15) for sb in stage_boxes],
            run_time=0.4,
        )

        self.wait(0.3)

        # ── Final callout ──
        callout_text = Text(
            "Entire diagnostic pipeline runs locally. Results in under 2 hours",
            font=FONT,
            font_size=21,
            color=GREEN,
            weight=BOLD,
        )
        callout_text.to_edge(DOWN, buff=0.25)

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