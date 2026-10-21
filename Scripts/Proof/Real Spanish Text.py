# this_file: Scripts/Proof/Real Spanish Text.py
# SPDX-License-Identifier: Apache-2.0
"""Open a new Glyph tab with five randomly chosen Spanish prose passages.

What it does:
    Draw five passages without replacement. Keep Spanish accents, punctuation
    and case, including a final space. No passage repeats in one proof.

How it works:
    Capture the current font, assemble the proof, then use the shared App
    text-tab helper with that font's id. Send missing characters unchanged.
    Refuse text that PythonQt cannot pass intact. No font data is written;
    no Undo step is needed. Tab creation can fail after a new tab opens.

Why this design:
    The native Glyph tab supplies an editable, non-modal proof. Run again for
    another sample. No separate panel or settings are needed. The 24 original
    passages below replace the upstream collection of 300 third-party excerpts.
    They include ñ, ü, accented vowels, inverted punctuation and figures.

How to use:
    Activate a font and run this command. Inspect spacing, accents and text
    colour in the new Glyph tab. Keep earlier tabs available for comparison.

Benefit:
    Test readable Spanish without finding and pasting external sample text.

Credit:
    Behaviour after Pedro Arilla, glyphs-scripts/Real* text/Real* Spanish text.py,
    Apache-2.0, https://github.com/pedroarilla/glyphs-scripts.
    Independent behaviour-only rewrite. No source code or corpus was copied.
    Proof passages are original to this tool, Apache-2.0.
"""

import random

TITLE = "Real Spanish Text"
DRAW_COUNT = 5
PASSAGES: tuple[str, ...] = (
    "Al abrir la panadería, Lucía encontró una cesta de limones junto a la puerta. No había ninguna nota, pero reconoció el pañuelo azul de su vecina.",
    "¿A qué hora sale el último autobús? El conductor consultó el reloj y sonrió: todavía quedaban veinte minutos para tomar un café en la plaza.",
    "«¡Qué alegría verte por aquí!», dijo la librera. Había guardado un pequeño atlas bajo el mostrador, envuelto en papel amarillo y atado con un cordel.",
    "El museo abre los sábados a las 10:30. La entrada cuesta 8,50 € e incluye una visita al jardín, donde crecen árboles de más de cien años.",
    "La cigüeña regresó al campanario a principios de marzo. Los niños levantaron la vista y siguieron su vuelo hasta que desapareció detrás del tejado.",
    "En el taller había veintitrés cajones, cada uno con su etiqueta. Andrés buscó una bisagra y encontró, por casualidad, la llave del antiguo armario.",
    "La lluvia borró parte del dibujo que habíamos hecho con tiza. Aun así, se distinguían el río, las montañas y un puente demasiado pequeño para el tren.",
    "Mañana llevaremos tortillas, tomates y una botella de agua. Si el día está despejado, subiremos hasta el mirador antes de sentarnos a comer.",
    "«No tengas prisa», aconsejó la jardinera. «Las semillas no entienden de calendarios». Después cerró el invernadero y se fue a preparar una infusión.",
    "El billete de ida y vuelta vale 24 €. Con la reserva anticipada se aplica un descuento del 15%; conviene conservar el recibo hasta el final del viaje.",
    "Beatriz había apuntado tres preguntas en el margen del cuaderno. Durante la reunión respondió a dos, pero la tercera abrió una conversación mucho más larga.",
    "Desde el balcón se veía una franja del puerto. Por la noche, las luces de los barcos parecían ventanas de una ciudad que se movía lentamente.",
    "El cine del barrio tiene 96 butacas y una cortina roja. Los jueves cambia la programación; los domingos, alguien trae bizcocho para compartir.",
    "¿Dónde dejaste las gafas? Quizá estén junto al periódico, debajo de la bufanda o en ese bolsillo donde siempre aparecen las cosas que damos por perdidas.",
    "Para coser el bolsillo, elige un hilo un poco más oscuro que la tela. Unas puntadas pequeñas bastarán para sujetarlo sin que pierda su forma.",
    "El guía explicó que aquel sendero tenía 2,5 kilómetros. Parecía una distancia corta, aunque la subida y el barro nos obligaron a caminar despacio.",
    "Habíamos comprado doce huevos para el desayuno de seis personas. La más pequeña pidió el pan tostado en triángulos y la pera cortada en estrellas.",
    "Al bajar la marea, aparece un paso de arena entre las dos playas. Es un buen lugar para observar cangrejos, siempre que se respete su refugio.",
    "La revista reúne relatos breves y dibujos de artistas del barrio. El número 4 incluye un mapa desplegable y una entrevista sobre los jardines públicos.",
    "¡Por fin llegó el paquete! Dentro había una taza verde, dos fotografías y una carta tan larga que decidimos leerla después de la cena.",
    "El pingüino del dibujo llevaba un paraguas diminuto. Según la niña que lo había pintado, no temía al agua: simplemente prefería caminar a la sombra.",
    "En la sala de espera solo habían cambiado las flores. Un pétalo de lirio descansaba junto al periódico y el reloj seguía adelantando cinco minutos.",
    "Tomás midió la estantería dos veces antes de cortar la tabla. Encajó a la primera, para sorpresa de todos menos de quien había revisado las medidas.",
    "Cuando cerraron el mercado, quedó una naranja sobre el banco de piedra. Una mujer la recogió, buscó a su dueño y acabó dejándola en la frutería.",
)


def proof_text() -> str:
    """Sample five distinct passages; preserve the final separating space."""
    if not PASSAGES:
        raise ValueError("No proof passages are available.")
    if any(c in passage for passage in PASSAGES for c in ("\0", "\u00a0", "\u2028", "\u2029")):
        raise ValueError("Unsupported proof character; text cannot pass intact.")
    return " ".join(random.sample(PASSAGES, DRAW_COUNT)) + " "


def run() -> None:
    """Build a proof only with an open font; delegate native tab ownership."""
    import fly.ap.scripting as context
    import fly.ap.text_tab as tabs

    package = context.current_package()
    if package is None:
        raise ValueError("Open a font before creating a prose proof.")
    package_id = int(package.id)
    tabs.open_text_tab(proof_text(), expected_id=package_id)


def main() -> None:
    """Menu entry; report a refusal without retrying native tab creation."""
    try:
        run()
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
