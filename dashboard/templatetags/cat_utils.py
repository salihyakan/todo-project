from django import template
from django.utils.safestring import mark_safe
import random

register = template.Library()

# Boyut mapping - CSS class ve piksel değerleri
SIZE_MAP = {
    'xs': 'cat-size-xs',
    'sm': 'cat-size-sm', 
    'md': 'cat-size-md',
    'lg': 'cat-size-lg',
    'xl': 'cat-size-xl',
    'xxl': 'cat-size-xxl'
}

# Konumlandırma mapping
POSITION_MAP = {
    # Fixed positions
    'fixed-tl': 'cat-fixed cat-fixed-top-left',
    'fixed-tr': 'cat-fixed cat-fixed-top-right',
    'fixed-tc': 'cat-fixed cat-fixed-top-center',
    'fixed-ml': 'cat-fixed cat-fixed-middle-left',
    'fixed-mr': 'cat-fixed cat-fixed-middle-right', 
    'fixed-mc': 'cat-fixed cat-fixed-middle-center',
    'fixed-bl': 'cat-fixed cat-fixed-bottom-left',
    'fixed-br': 'cat-fixed cat-fixed-bottom-right',
    'fixed-bc': 'cat-fixed cat-fixed-bottom-center',
    
    # Relative positions
    'relative-tl': 'cat-relative cat-relative-top-left',
    'relative-tr': 'cat-relative cat-relative-top-right',
    'relative-tc': 'cat-relative cat-relative-top-center',
    'relative-ml': 'cat-relative cat-relative-middle-left',
    'relative-mr': 'cat-relative cat-relative-middle-right',
    'relative-mc': 'cat-relative cat-relative-middle-center',
    'relative-bl': 'cat-relative cat-relative-bottom-left',
    'relative-br': 'cat-relative cat-relative-bottom-right',
    'relative-bc': 'cat-relative cat-relative-bottom-center',
    
    # Inline positions
    'inline-before': 'cat-inline cat-inline-before',
    'inline-after': 'cat-inline cat-inline-after',
    'inline-top': 'cat-inline cat-inline-top',
    'inline-middle': 'cat-inline cat-inline-middle',
    'inline-bottom': 'cat-inline cat-inline-bottom'
}

# Efekt mapping
EFFECT_MAP = {
    'float': 'cat-float',
    'bounce': 'cat-bounce',
    'pulse': 'cat-pulse',
    'rotate': 'cat-rotate',
    'shake': 'cat-shake',
    'none': ''
}

@register.simple_tag
def cat_image(image_name, position='fixed-tr', size='md', effect='float', custom_class='', custom_style='', clickable=True):
    """
    Gelişmiş kedi resmi - Konuşma balonu özellikli
    
    Parameters:
    - image_name: kedo-1.png, kedo-2.png, etc.
    - position: fixed-tr, relative-tl, inline-before, etc.
    - size: xs, sm, md, lg, xl, xxl veya direkt piksel değeri (50px)
    - effect: float, bounce, pulse, rotate, shake, none
    - custom_class: ek CSS class'ları
    - custom_style: inline CSS
    - clickable: tıklanabilir olsun mu? (Varsayılan: True)
    """
    
    # Boyut belirleme
    if size in SIZE_MAP:
        size_class = SIZE_MAP[size]
        inline_size = ''
    else:
        # Direkt piksel değeri
        size_class = ''
        inline_size = f'width: {size};'
    
    # Konumlandırma
    position_class = POSITION_MAP.get(position, POSITION_MAP['fixed-tr'])
    
    # Efekt
    effect_class = EFFECT_MAP.get(effect, EFFECT_MAP['float'])
    
    # Tıklanabilirlik - Varsayılan True
    clickable_class = 'cat-clickable' if clickable else ''
    
    html = f'''
    <div class="{position_class} {size_class} {effect_class} {clickable_class} {custom_class}" 
         style="{custom_style}">
        <img src="/static/images/{image_name}" 
             alt="Sevimli Kedi" 
             class="cat-image"
             style="{inline_size}">
    </div>
    '''
    
    return mark_safe(html)

@register.simple_tag
def random_cat(position='fixed-tr', size='md', effect='float'):
    """Rastgele kedi resmi"""
    cat_number = random.randint(1, 21)
    image_name = f'kedo-{cat_number}.png'
    
    return cat_image(image_name, position, size, effect)

@register.simple_tag
def conditional_cat(condition=True, **kwargs):
    """Koşula bağlı kedi gösterimi"""
    if condition:
        return cat_image(**kwargs)
    return ''

# Hızlı kullanım için özel tag'ler
@register.simple_tag
def cat_fixed(image_name, corner='tr', size='md', effect='float'):
    """Hızlı fixed kedi"""
    position = f'fixed-{corner}'
    return cat_image(image_name, position, size, effect)

@register.simple_tag
def cat_relative(image_name, corner='tr', size='md', effect='float'):
    """Hızlı relative kedi"""
    position = f'relative-{corner}'
    return cat_image(image_name, position, size, effect)

@register.simple_tag
def cat_inline(image_name, where='before', size='sm', effect='none'):
    """Hızlı inline kedi"""
    position = f'inline-{where}'
    return cat_image(image_name, position, size, effect)