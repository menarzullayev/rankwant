"""Unvon darajasi va ijtimoiy maydonlar — ADR-0026.

To'rtta ustun qo'shiladi: `rank_title`, `max_rank_title`, `friend_count`,
`title_photo_url`. Ular Codeforces'dagi `rank`, `maxRank`, `friendOfCount`,
`titlePhoto` maydonlarining ekvivalenti.

NOM ATAYLAB NEYTRAL. Codeforces maydoni — raqobatchining nomi, va ADR-0014
uni schema darajasiga kiritishni rad etgan: u holda har so'rov, serializer va
migration unga bog'lanib qolardi. ADR-0024 bu yo'lni `contribution` bilan
ochgan (Codeforces maydoni, neytral nom), bu to'rttasi shu qatorning davomi.
Manba ustun nomida emas, yozuvchi kodda saqlanadi — `sync_codeforces`.

`friend_count` (Codeforces `friendOfCount`) va `contribution` (ADR-0024)
hozircha FAQAT sinxron yozadigan maydonlar: ularning qiymati boshqa
platformadan keladi. O'z do'stlar/ovoz tizimimiz ishga tushganda ular shu
ustunlarni to'ldira boshlaydi va sinxron qiymati almashadi — ya'ni ustunning
ma'nosi kelajakda o'zgaradi, lekin nomi o'zgarmaydi. Shu sababli bu yerda
"manba" izohi muhim: u ma'noning almashishini kutayotganini ko'rsatadi.
"""

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0021_seed_staff_groups"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="rank_title",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="user",
            name="max_rank_title",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="user",
            name="friend_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="user",
            name="title_photo_url",
            field=models.URLField(blank=True, max_length=200),
        ),
    ]
