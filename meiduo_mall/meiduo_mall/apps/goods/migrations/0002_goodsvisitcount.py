# Generated by Django 4.1.7 on 2023-03-20 08:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoodsVisitCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('count', models.IntegerField(default=0, verbose_name='访问量')),
                ('date', models.DateField(auto_now_add=True, verbose_name='统计日期')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='goods.goodscategory', verbose_name='商品分类')),
            ],
            options={
                'verbose_name': '统计分类商品访问量',
                'verbose_name_plural': '统计分类商品访问量',
                'db_table': 'tb_goods_visit',
            },
        ),
        # migrations.RunSQL(
        #     """
        #     CREATE TABLE tb_goods_visit(
        #     create_time datetime(6) NOT NULL,
        #     update_time datetime(6) NOT NULL,
        #     id integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        #     count integer NOT NULL,
        #     date date NOT NULL,
        #     category_id int NOT NULL,
        #     CONSTRAINT tb_goods_visit_category_id_b3e36237_fk_tb_goods_category_id FOREIGN KEY(category_id) REFERENCES tb_goods_category(id)
        #      );
        #     """
        # ),
    ]
