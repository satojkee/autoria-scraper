"""This module contains all selectors used by scrapers."""


from typing import TypedDict, NotRequired


__all__ = (
    'PaginationSelectors',
    'ListedSelectors',
    'CarSelectors'
)


class _Selector(TypedDict):
    """Contains BS4 supported search params."""
    id: NotRequired[str]
    name: NotRequired[str]
    class_: NotRequired[str]
    attrs: NotRequired[dict]


class CarSelectors:
    """Selectors required for direct page processing."""
    # car vin number (possible None)
    # checked - regular, unchecked - extra
    vin_checked = _Selector(name='span', class_='label-vin')
    vin_unchecked = _Selector(name='span', class_='vin-code')
    # narrows price search scope
    price_container = _Selector(name='div', class_='price_value')
    # car price
    price = _Selector(name='strong')
    # car title ([-1] index in `.find_all`)
    title = _Selector(name='h1', class_='head')
    # car odometer
    odometer = _Selector(name='div', class_='base-information')
    # car seller username/name
    username = _Selector(class_='seller_info_name')
    # car state number (possible None)
    state_number = _Selector(name='span', class_='state-num')
    # narrows image count search scope ([0] index in `.find_all`)
    images_count_container = _Selector(name='span', class_='count')
    # car image count
    images_count = _Selector(name='span', class_='mhide')
    # car primary image 
    image_url = _Selector(name='source', attrs={'type': 'image/webp'})
    # required to obtain seller phone number (use data-value-id attr)
    phone_number_phone_id = _Selector(name='a', class_='popup-successful-call')
    # required to obtain seller phone number (use data-auto-id attr)
    phone_number_auto_id = _Selector(name='body')
    # to track listing status (in some cases, car page may be accessible but 
    #  not scrapable)
    unavailable = _Selector(name='div', class_='notice_head')
    

class PaginationSelectors:
    """Selectors required to discover total amount of pages."""
    # narrows search scope for pagination links
    container = _Selector(name='div', id='pagination')
    # pagination single link
    link = _Selector(name='span', class_='dhide')


class ListedSelectors:
    """Selectors required to extract links from each listing page."""
    link = _Selector(name='a', class_='m-link-ticket')
