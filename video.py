from manim import *


class SyntheticDataTopics(Scene):
    def construct(self) -> None:
        title = Text(
            "Yapay Veri Üretimi: Konu Üretme",
            weight=BOLD,
            font_size=35,
        )
        self.play(Write(title))
        self.wait(0.3)
        self.play(FadeOut(title))
        self.wait(0.5)

        paragraphs = [
            """
            Python programlama dili,
            basit sözdizimi ve güçlü
            kütüphaneleri sayesinde...
            """,
            """
            COVID-19 virüsü 2019 yılının
            sonlarında Çin'de ortaya
            çıktıktan sonra hızla tüm...
            """,
        ]

        topics = [
            "Python Dili",
            "COVID-19 Virüsü",
        ]

        gemma_box = RoundedRectangle(width=3, height=1, fill_color=BLUE, stroke_color=BLUE, fill_opacity=0.2, corner_radius=0.15)
        self.play(Write(gemma_box))
        self.play(Write(Text("Gemma 3 27B", font_size=25, color=WHITE)))
        self.wait(0.25)

        self.play(Write(Text("Paragraf:", font_size=30, color=WHITE).to_edge(LEFT).to_edge(UP)))
        self.wait(0.25)

        self.play(Write(Text("Konu:", font_size=30, color=WHITE).to_edge(RIGHT).to_edge(UP)))
        self.wait(0.25)

        for paragraph, topic in zip(paragraphs, topics):
            paragraph_text = Text(paragraph, font_size=18, color=WHITE).to_edge(LEFT)
            self.play(Write(paragraph_text))
            self.wait(0.25)
            
            # Arrow from paragraph to model
            arrow1 = Arrow(paragraph_text.get_right(), gemma_box.get_left(), color=YELLOW)
            self.play(Create(arrow1))
            self.wait(0.25)
            
            topic_text = Text(topic, font_size=28, color=WHITE).to_edge(RIGHT)
            
            # Arrow from model to topic
            arrow2 = Arrow(gemma_box.get_right(), topic_text.get_left(), color=YELLOW)
            self.play(Create(arrow2))
            self.wait(0.25)
            
            self.play(Write(topic_text))
            self.wait(0.25)
            
            self.play(FadeOut(paragraph_text), FadeOut(topic_text), FadeOut(arrow1), FadeOut(arrow2))
            self.wait(0.25)

        ###################################################

        self.play(*[FadeOut(mob) for mob in self.mobjects])
        self.wait(0.5)

        ###################################################

        title = Text(
            "Yapay Veri Üretimi: Eğitim Materyali Üretme",
            weight=BOLD,
            font_size=35,
            color=WHITE,
        )
        self.play(Write(title))
        self.wait(0.3)
        self.play(FadeOut(title))
        self.wait(0.5)

        topics = [
            "Python Dili",
            "COVID-19 Virüsü",
        ]

        materials = [
            """
            Python, 1991 yılında
            Guido van Rossum...
            """,
            """
            COVID-19 Virüsü,
            İlk kez 2019 yılının...
            """,
        ]

        claude_box = RoundedRectangle(width=3, height=0.9, fill_color=BLUE, stroke_color=BLUE, fill_opacity=0.2, corner_radius=0.15)
        self.play(Write(claude_box))
        claude_text = Text("Claude 4 Sonnet", font_size=25, color=WHITE)
        self.play(Write(claude_text))
        self.wait(0.25)

        konu_text = Text("Konu:", font_size=30, color=WHITE).to_edge(LEFT).to_edge(UP)
        self.play(Write(konu_text))
        self.wait(0.25)

        materyal_text = Text("Eğitim Materyali:", font_size=30, color=WHITE).to_edge(RIGHT).to_edge(UP)
        self.play(Write(materyal_text))
        self.wait(0.25)

        for topic, material in zip(topics, materials):
            topic_text = Text(topic, font_size=28, color=WHITE).to_edge(LEFT)
            self.play(Write(topic_text))
            self.wait(0.25)

            # Arrow from topic to claude
            arrow1 = Arrow(topic_text.get_right(), claude_box.get_left(), color=YELLOW)
            self.play(Create(arrow1))
            self.wait(0.25)

            material_text = Text(material, font_size=18, color=WHITE).to_edge(RIGHT)

            # Arrow from claude to material
            arrow2 = Arrow(claude_box.get_right(), material_text.get_left(), color=YELLOW)
            self.play(Create(arrow2))
            self.wait(0.25)

            self.play(Write(material_text))
            self.wait(0.25)
            
            if topic != topics[-1]:
                self.play(FadeOut(topic_text), FadeOut(material_text), FadeOut(arrow1), FadeOut(arrow2))
                self.wait(0.50)

        ###################################################

        self.play(*[FadeOut(mob) for mob in self.mobjects])
        self.wait(0.5)

        ###################################################

        title = Text(
            "Yapay Zeka Eğitimi",
            weight=BOLD,
            font_size=35,
            color=WHITE,
        )
        self.play(Write(title))
        self.wait(0.3)
        self.play(FadeOut(title))
        self.wait(0.5)

        veri_kumesi_text = Text("Veri Kümesi:", font_size=26, color=WHITE).to_edge(LEFT).to_edge(UP)
        self.play(Write(veri_kumesi_text))
        self.wait(0.25)

        # Dataset block on the left
        dataset_box = RoundedRectangle(
            width=4,
            height=2.8,
            corner_radius=0.2,
            color=RED,
            fill_color=RED,
            fill_opacity=0.1,
        ).shift(4 * LEFT).to_edge(LEFT)
        self.play(Write(dataset_box))
        self.wait(0.25)

        dataset_text = Text("""
            Girdi: Konu

            Çıktı: Eğitim Materyali
            """, font_size=22, color=WHITE).move_to(dataset_box.get_center())
        self.play(Write(dataset_text))
        self.wait(0.25)

        gemma_box = RoundedRectangle(width=2.5, height=0.9, fill_color=BLUE, stroke_color=BLUE, fill_opacity=0.2, corner_radius=0.15)

        arrow = Arrow(dataset_box.get_right(), gemma_box.get_left(), color=YELLOW)
        self.play(Create(arrow))
        self.wait(0.25)

        self.play(Write(gemma_box))
        self.play(Write(Text("Gemma 2 9B", font_size=20, color=WHITE)))
        self.wait(0.25)

        ogrenix_box = RoundedRectangle(width=2.5, height=0.9, fill_color=GREEN, stroke_color=GREEN, fill_opacity=0.2, corner_radius=0.15).to_edge(RIGHT)

        arrow = Arrow(gemma_box.get_right(), ogrenix_box.get_left(), color=YELLOW)
        self.play(Create(arrow))
        self.wait(0.25)
        
        self.play(Write(ogrenix_box))
        self.play(Write(Text("Öğrenix Model", font_size=20, color=WHITE).move_to(ogrenix_box.get_center())))
        self.wait(0.25)

        ###################################################

        self.play(*[FadeOut(mob) for mob in self.mobjects])
        self.wait(0.5)

        ###################################################

        title = Text(
            "Öğrenix Uygulaması",
            weight=BOLD,
            font_size=35,
            color=WHITE,
        )
        self.play(Write(title))
        self.wait(0.3)
        self.play(FadeOut(title))
        self.wait(0.5)

        ogrenix_box = RoundedRectangle(width=2.5, height=0.9, fill_color=GREEN, stroke_color=GREEN, fill_opacity=0.2, corner_radius=0.15)
        self.play(Write(ogrenix_box))
        self.play(Write(Text("Öğrenix Model", font_size=20, color=WHITE).move_to(ogrenix_box.get_center())))
        self.wait(0.25)

        ozel_istem = Text("Özel istem:", font_size=20, color=WHITE).to_edge(LEFT).to_edge(UP).shift(2.3 * DOWN).shift(1 * RIGHT)
        self.play(Write(ozel_istem))
        self.wait(0.25)

        prompt_box = RoundedRectangle(
            width=3.5,
            height=3.5,
            corner_radius=0.2,
            color=RED,
            fill_color=RED,
            fill_opacity=0.1,
        ).to_edge(LEFT).shift(1 * DOWN)
        self.play(Write(prompt_box))
        self.wait(0.25)

        prompt_text = Text("""
            Aşağıdaki konuyu
            ayrıntılı ve anlaşılır
            bir şekilde anlat...

            Konu:
            """, font_size=21, color=WHITE).move_to(prompt_box.get_center()).shift(0.7 * UP)
        self.play(Write(prompt_text))

        prompt_text_bottom = Text("""
            Özel formatları
            aşağıdaki şekilde...
            """, font_size=21, color=WHITE).move_to(prompt_box.get_center()).shift(1.2 * DOWN).shift(0.14 * LEFT)
        self.play(Write(prompt_text_bottom))
        self.wait(0.25)

        girilen_konu = Text("Girilen konu:", font_size=20, color=WHITE).to_edge(LEFT).to_edge(UP).shift(0.8 * RIGHT).shift(0.5 * DOWN)
        self.play(Write(girilen_konu))
        self.wait(0.25)

        konu_box = Rectangle(width=3.5, height=0.5, fill_color=BLUE, stroke_color=BLUE, fill_opacity=0.1).to_edge(LEFT).to_edge(UP).shift(1 * DOWN)
        self.play(Write(konu_box))

        konu_text = Text("Karadelikler nasıl oluşur?", font_size=18, color=WHITE).move_to(konu_box.get_center())
        self.play(Write(konu_text))
        self.wait(0.25)

        self.play(FadeOut(girilen_konu))

        self.play(
            konu_box.animate.scale(0.85).move_to(prompt_box.get_center()).shift(0.35 * DOWN),
            konu_text.animate.scale(0.85).move_to(prompt_box.get_center()).shift(0.35 * DOWN)
        )
        self.wait(0.5)

        arrow = Arrow(prompt_box.get_right(), ogrenix_box.get_left(), color=YELLOW)
        self.play(Create(arrow))
        self.wait(0.25)

        output_box = RoundedRectangle(
            width=3.5,
            height=6,
            corner_radius=0.2,
            color=BLUE,
            fill_color=BLUE,
            fill_opacity=0.1,
        ).to_edge(RIGHT)

        arrow_2 = Arrow(ogrenix_box.get_right(), output_box.get_left(), color=YELLOW)
        self.play(Create(arrow_2))
        self.wait(0.25)

        self.play(Write(output_box))
        self.play(Write(Text("Çıktı:", font_size=20, color=WHITE).to_edge(RIGHT).to_edge(UP).shift(1.45 * LEFT)))
        self.wait(0.25)

        output_text1 = Text("""
            Karadelik,
            uzay-zamanın öyle bir
            bölgesidir ki
            ışık bile oradan...
            """, font_size=19, color=WHITE).move_to(output_box.get_center()).shift(2.2 * UP)
        self.play(Write(output_text1))
        self.wait(0.25)

        graph_box = RoundedRectangle(
            width=3,
            height=1.75,
            corner_radius=0.1,
            color=GREEN,
            fill_color=GREEN,
            fill_opacity=0.1,
        ).move_to(output_box.get_center()).shift(0.6 * UP)
        self.play(Write(graph_box))
        self.wait(0.25)

        # Create the orbiting animation inside the green box
        big_circle = Circle(radius=0.2, color=YELLOW, fill_opacity=0.8).move_to(graph_box.get_center())
        small_circle = Circle(radius=0.08, color=WHITE, fill_opacity=1).move_to(graph_box.get_center() + 0.5 * RIGHT)
        tiny_circle = Circle(radius=0.03, color=BLUE, fill_opacity=1).move_to(small_circle.get_center() + 0.2 * RIGHT)
        
        self.play(Create(big_circle), Create(small_circle), Create(tiny_circle))
        
        # Create the orbiting animation
        orbit_radius = 0.5
        orbit_center = graph_box.get_center()
        
        # Store initial time to maintain consistent orbit starting position
        start_time = self.renderer.time
        
        def orbit_updater(mob, dt):
            angle = (self.renderer.time - start_time) * 2  # Control speed of orbit
            new_pos = orbit_center + orbit_radius * np.array([np.cos(angle), np.sin(angle), 0])
            mob.move_to(new_pos)
        
        def tiny_orbit_updater(mob, dt):
            angle = (self.renderer.time - start_time) * 6  # Faster orbit around white circle
            tiny_orbit_radius = 0.2
            new_pos = small_circle.get_center() + tiny_orbit_radius * np.array([np.cos(angle), np.sin(angle), 0])
            mob.move_to(new_pos)
        
        small_circle.add_updater(orbit_updater)
        tiny_circle.add_updater(tiny_orbit_updater)

        self.wait(1)

        dotdotdot = Text(".......", font_size=22, color=WHITE).move_to(graph_box.get_center()).shift(2 * DOWN)
        self.play(Write(dotdotdot))
        self.wait(2)

        small_circle.remove_updater(orbit_updater)
        tiny_circle.remove_updater(tiny_orbit_updater)

        self.play(*[FadeOut(mob) for mob in self.mobjects])
        self.wait(0.5)
