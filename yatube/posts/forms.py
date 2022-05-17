from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Текст', 'group': 'Группа', 'image': 'Картинка'}
        help_texts = {'text': "Текст вашего поста",
                      'group': "Группа к которой, относиться ваш пост",
                      'image': "Изображение к посту",
                      }

    def clean_text(self):
        data = self.cleaned_data['text']
        if 'проверка' not in data.lower():
            raise forms.ValidationError('Вы обязательно должны '
                                        'проверить пост!')

        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = {'text'}
        labels = {'text': 'Текст'}
        help_texts = {'text': "Текст вашего комментария"}

    def clean_text(self):
        data = self.cleaned_data['text']
        if 'бяка' in data.lower():
            raise forms.ValidationError('Комментарий не должен содержать '
                                        'нецензурных выражений!')

        return data
