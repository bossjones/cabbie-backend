import datetime

from cabbie.common.admin import DateRangeFilter

class EndDateIncludingDateRangeFilter(DateRangeFilter):
    def queryset(self, request, queryset):
        if self.form.is_valid():
            # get no null params
            filter_params = dict(filter(lambda x: bool(x[1]),
                                        self.form.cleaned_data.items()))

            end_filter = filter_params.get('{0}__lte'.format(self.field_path))
            if end_filter:
                end_filter = end_filter + datetime.timedelta(days=1)
                filter_params['{0}__lte'.format(self.field_path)] = end_filter

            return queryset.filter(**filter_params)
        else:
            return queryset
