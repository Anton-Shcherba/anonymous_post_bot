voice_dict: dict[str, str] = {
    "AwACAgIAAxkBAAPyZWhwWIcbnRH_mzGMcOrjsJcwznAAAlI8AALe1kFLZIakUwrz07kzBA": "🍯 м, сука ну мед, мед блядь, ну медятина, мед",
    "AwACAgIAAxkBAAP2ZWh14EAqw7pB22Xi7wWA5a3VLE8AAlM9AALMIUBLyGwEWa-ikPkzBA": "🌩️ ха-ха, конечно, конечно, конечно",
    "AwACAgIAAxkBAAP6ZWh5m0lKejwrl-mxS5sdOJem018AAqk9AALMIUBLRda--w1ZHjYzBA": "👵 ну и что, перед каждым отчитываться я буду, перед вами блядями",
    "AwACAgIAAxkBAAP-ZWh8J_WQQ1pdixHPfrh_YIFlG9YAAuk9AALMIUBLtRrf4ET_7oUzBA": "🐶 ты и как телка стремный, но как собака заебись, все давай, иди нахуй",
    "AwACAgIAAxkBAAIBAmVofquf0JeK1D41NQOd4-wJSny9AAIWPgACzCFAS2mrixLb9sCxMwQ": "💀 а вдруг я завтра сдохну, правильно",
    "AwACAgIAAxkBAAIBBmVogAeOSvjXo4Y96Rvn5P2hbYbPAAIbPgACzCFAS0UQUxDmwHd4MwQ": "🤝 здарова заебал",
    "AwACAgIAAxkBAAIBCmVogKsMsg5mFqFhxA0JrZI7c1NmAAIoPgACzCFAS2LzOQnWjbgaMwQ": "🐀 ля ты крыса",
    "AwACAgIAAxkBAAIBDmVogeJb1jsyYPtP-JXbZ0bh0txSAAJHPgACzCFAS0UYjzWS3kCiMwQ": "👋 всего хоро шего",
    "AwACAgIAAxkBAAIBEmVogswfKCal4k4ao3jrKfiDbd--AAJXPgACzCFASxk3FC7YqS6VMwQ": "😮 да ну нахуй",
    "AwACAgIAAxkBAAIBFmVogw_TeyA9E1qDI_yn8fk3FbPiAAJbPgACzCFAS22i_eApqR7sMwQ": "😱 cтрашно, очень страшно, мы не знаем что это такое, если бы мы знали что это такое, мы не знаем что это такое",
    "AwACAgIAAxkBAAIBGmVog54oXQZ3cMv8TdWrjFYlZC1TAAJhPgACzCFAS6C_YfB9RnrbMwQ": "😴 бля, иди поспи нахуй, реально, вот иди приляг нахуй и поспи",
    "AwACAgIAAxkBAAIBHmVohGB0f4XkDwSKJdy7-098WrwyAAJ3PgACzCFAS1vFbe-WCHduMwQ": "🧐 вы кто такие, я вас не звал, идите нахуй",
    "AwACAgIAAxkBAAIBJGVoiVJOsEHo_TpDp920oYahesTrAAKzPgACzCFAS6Dp8c9xKnfwMwQ": "❌ не, нихуя",
    "AwACAgIAAxkBAAIBKGVolMdmK5Dl5tb4UNWAZ5AYYAMgAAL-PgACzCFAS1xFyK7vmmP7MwQ": "🤩 oh my god, wow",
    "AwACAgIAAxkBAAIBLGVolRg9IxiCWH73Ld6vMNaarmnaAAIBPwACzCFAS80pPuoY_yLoMwQ": "🍼 вот типичныи пример малолетнего дебила",
    "AwACAgIAAxkBAAIBMGVolVJitUkKdubzGP8gZLPuLDsnAAIEPwACzCFASw6AdbuHpXyXMwQ": "🚗 вот это поворот",
    "AwACAgIAAxkBAAIBNGVolX_-n6MTNP0AARCISu1uJH0d3gACBz8AAswhQEt81IYQ03hh8zME": "😬 это фиаско, братан",
    "AwACAgIAAxkBAAIBOGVolbyPGtWtVMl-XYzyyx2KeeByAAILPwACzCFAS2w_Iudp3418MwQ": "🍖 вставай, заебал ты, ебаный шашлык",
    "AwACAgIAAxkBAAIBPGVolepgEVJU-6Vv9GUpPBlBMe3QAAIOPwACzCFAS_zvDj5TX2-9MwQ": "🏃‍♂️ беги сука беги",
    "AwACAgIAAxkBAAIBQGVollddCKWLlS9ZPmhXL8pOZwMfAAIRPwACzCFASwqIhymOrsSaMwQ": "👏 я просто похлопаю, ха-ха",
    "AwACAgIAAxkBAAIBRGVoloAGCkJpLWl5ObAzXj7ZzLA6AAIVPwACzCFAS05WNvpybDXpMwQ": "😐 мне что-то подсказывает что нас наебали",
    "AwACAgIAAxkBAAIBSGVolqpvELuIRYCG9UZZ9PKDbYLmAAIZPwACzCFASyEAAZV_DWzyvDME": "🎖 лох, пидр",
    "AwACAgIAAxkBAAIBTGVoltv8b0EolIhxVC7GvacoAiSRAAIdPwACzCFASyAWRVqJ99WcMwQ": "👻 ну нахер",
    "AwACAgIAAxkBAAIBUGVolwI-zB1LXA8nVzWRUfBauyYCAAIhPwACzCFAS5pgjodIe81GMwQ": "👴 да ладно",
    "AwACAgIAAxkBAAIBVGVolz9PeN_-SCTQMKRHWPhjWiBYAAIkPwACzCFASxkcuP7ImQhPMwQ": "👹 найн, найн, найн, найн, найн, найн, найн",
    "AwACAgIAAxkBAAIBWGVol2lKMkIsChwRF-Z45dkvTwvvAAIpPwACzCFAS8SjhFm9fY_uMwQ": "💅 пиздец нахуй блядь",
    "AwACAgIAAxkBAAIBXGVol5_7BOEzgv0M6ofcD_1r2_AAAy0_AALMIUBL8JEsT46d0p4zBA": "☝ но это не точно",
    "AwACAgIAAxkBAAIBYGVomCie0BQy-ZIYTKg0eCquQZ0bAAI0PwACzCFASzHH3dQ44Wx3MwQ": "😆 ха-ха, вот ты меня расмешнил, расмешнил, расмешнила, рассмеялась",
    "AwACAgIAAxkBAAIBZGVomFwT1_nmHlQJXUPnZ2L9YK2tAAI5PwACzCFASyQn9pZn86kEMwQ": "👶 hello, motherfucker",
    "AwACAgIAAxkBAAIBaGVomJBUqv8huy7VnsLXnkcWCzfNAAI9PwACzCFAS2wjDuo1WMDxMwQ": "💩 я хочу какать",
    "AwACAgIAAxkBAAIBbGVomMLrRFCy5G-IwiSGvu4DiIzXAAJCPwACzCFAS503TnZ05WXxMwQ": "👌 а, понимаю",
    "AwACAgIAAxkBAAIBcGVomU46y38lULwFUL64hD0hy3mYAAJIPwACzCFAS_n59RUFtR8DMwQ": "🚬 здарова братиш",
    "AwACAgIAAxkBAAIBdGVomXKPbUs21c2MdBEUfnyfDiEpAAJLPwACzCFAS22pSomY-Z8ZMwQ": "🙈 ты втираешь мне какую-то дичь",
    "AwACAgIAAxkBAAIBeGVomZklQb9kM3itH9X-Cw3Iq9eTAAJNPwACzCFAS0uO2mJa2bmMMwQ": "🤩 вот это прикол",
    "AwACAgIAAxkBAAIBfGVomcZoBTmXtLj_yrPdf9ts9v2fAAJRPwACzCFAS9671jVNqM2QMwQ": "🙊 да что ты черт побери такое несешь",
    "AwACAgIAAxkBAAIBgGVomf0AAVlsTp0ute-HNaI7QA7DuQACVz8AAswhQEsNQ3TrZw3SGDME": "👽 но делать это я конечно же не буду",
    "AwACAgIAAxkBAAIBhGVominG5gjXEWHZ1AuL7x9MIhR6AAJaPwACzCFAS0CUYbtqPg_YMwQ": "🛸 сильное заявление, проверять я его конечно не буду",
    "AwACAgIAAxkBAAIBiGVomlYMJOcLmAuOaVOii_PsHBbtAAJcPwACzCFASz9ghMeQm36jMwQ": "☀ утро доброе блядь",
    "AwACAgIAAxkBAAIBjGVoms5jYkTyHr5bl91eDb8qgZ1SAAJhPwACzCFAS6Ipi8qxNC6wMwQ": "🤠 давай по новой миша, всё хуйня",
    "AwACAgIAAxkBAAIBkGVomweh4xvsSRtLfFgaScuIycDcAAJjPwACzCFASxZHeoE_630LMwQ": "🏎 о да, маквин готов",
    "AwACAgIAAxkBAAIBlGVom0Quh5H3cakob-5jgeoyX37QAAJoPwACzCFASwJ4eQiX9EveMwQ": "🙆‍♂️ о боже мой, да всем насрать",
    "AwACAgIAAxkBAAIBmGVom3PYxk0DgF4pCQVx2evMckHxAAJpPwACzCFASxdtJPO84ZK1MwQ": "👍 это, просто, ахуенно",
    "AwACAgIAAxkBAAIBnGVom51TMyobTlsiMqkZJi5vJs9wAAJtPwACzCFAS8-Z5d1UQYtDMwQ": "😢 я с тобой не вожусь, я стобой не разговариваю, я стобой не общаюсь, я обиделся, ты меня обидел, не стыдно тебе",
    "AwACAgIAAxkBAAIBoGVom_PzlRsJIh4h2jKJ1xCbQ45dAAJxPwACzCFAS76tRDY7XRY6MwQ": "👙 а ты пизда ехидная не улыбайся, блядь щас как поддам под пизду",
    "AwACAgIAAxkBAAIBpGVonCuhCXYrmo-M48fLZUXvYWBwAAJzPwACzCFASyIFPdAvyeHUMwQ": "👱‍♀️ и что, и что, ну и че типо с этого",
    "AwACAgIAAxkBAAIBqGVonFOLLn7TVbRwCxalt1fYgZu7AAJ0PwACzCFAS0hZT6Bps-2IMwQ": "😘 не расстраивайся",
    "AwACAgIAAxkBAAPvZWhbSvro4o11fJu-9gzP78KkWTMAAoU7AALe1kFL-6hYymGxPdEzBA": "🏁 я сказала стартуем",
    "AwACAgIAAxkBAAIBrmVonIGTUYcHTI_uMJXLOZBuD55DAAJ4PwACzCFASzpDmIOjOA6UMwQ": "🔎 чтооо",
}