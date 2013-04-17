# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView, DetailView, ListView
from getpaid.forms import PaymentMethodForm
from .forms import DummyForm
from .models import Offer, Spent, Funding


def mix(*streams):
    substreams = []
    for stream, read_date, tag in streams:
        iterstream = iter(stream)
        try:
            item = next(iterstream)
        except StopIteration:
            pass
        else:
            substreams.append([read_date(item), item, iterstream, read_date, tag])
    while substreams:
        i, substream = max(enumerate(substreams), key=lambda x: x[1][0])
        yield substream[4], substream[1]
        try:
            item = next(substream[2])
        except StopIteration:
            del substreams[i]
        else:
            substream[0:2] = [substream[3](item), item]


class WLFundView(TemplateView):
    template_name = "funding/wlfund.html"

    def get_context_data(self):
        def add_total(total, it):
            for tag, e in it:
                e.total = total
                if tag == 'spent':
                    total += e.amount
                else:
                    total -= e.wlfund
                yield tag, e

        ctx = super(WLFundView, self).get_context_data()
        offers = []
        for o in Offer.objects.all():
            if o.state() == 'lose':
                o.wlfund = o.sum()
                if o.wlfund > 0:
                    offers.append(o)
            elif o.state() == 'win':
                o.wlfund = o.sum() - o.target
                if o.wlfund > 0:
                    offers.append(o)
        amount = sum(o.wlfund for o in offers) - sum(o.amount for o in Spent.objects.all())
        print offers

        ctx['amount'] = amount
        ctx['log'] = add_total(amount, mix(
            (offers, lambda x: x.end, 'offer'),
            (Spent.objects.all(), lambda x: x.timestamp, 'spent'),
        ))
        return ctx


class OfferDetailView(FormView):
    form_class = DummyForm
    template_name = "funding/offer_detail.html"

    def dispatch(self, request, slug=None):
        if slug:
            self.object = get_object_or_404(Offer.public(), slug=slug)
        else:
            self.object = Offer.current()
            if self.object is None:
                raise Http404
        return super(OfferDetailView, self).dispatch(request, slug)

    def get_form(self, form_class):
        if self.request.method == 'POST':
            return form_class(self.object, self.request.POST)
        else:
            return form_class(self.object, initial={'amount': settings.FUNDING_DEFAULT})

    def get_context_data(self, *args, **kwargs):
        ctx = super(OfferDetailView, self).get_context_data(*args, **kwargs)
        ctx['object'] = self.object
        if self.object.is_current():
            ctx['funding_no_show_current'] = True
            ctx['payment_form'] = PaymentMethodForm('PLN', initial={'order': self.object})
        return ctx

    def form_valid(self, form):
        funding = form.save()
        return redirect(funding.get_absolute_url())


class OfferListView(ListView):
    queryset = Offer.public()

    def get_context_data(self, *args, **kwargs):
        ctx = super(OfferListView, self).get_context_data(*args, **kwargs)
        ctx['funding_no_show_current'] = True
        return ctx


class FundingView(DetailView):
    model = Funding

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(FundingView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super(FundingView, self).get_context_data(*args, **kwargs)
        if self.object.offer.is_current():
            ctx['funding_no_show_current'] = True
            ctx['payment_form'] = PaymentMethodForm('PLN', initial={'order': self.object})
        return ctx

