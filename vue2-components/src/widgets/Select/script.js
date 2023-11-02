import { COMPUTED } from '../../core/utils';

function addLabels(values, allTextValues) {
  const result = [];
  const labelMap = {};
  for (let i = 0; i < allTextValues.length; i++) {
    const { text, value } = allTextValues[i];
    labelMap[value] = text;
  }
  for (let i = 0; i < values.length; i++) {
    const value = values[i];
    const text = labelMap[value] || `${value}`;
    result.push({ text, value });
  }
  return result;
}

export default {
  name: 'swSelect',
  props: {
    name: {
      type: String,
    },
    size: {
      type: Number,
      default: 1,
    },
    label: {
      type: String,
    },
    help: {
      type: String,
    },
    mtime: {
      type: Number,
    },
    type: {
      type: String,
    },
    initial: {},
    // -- add-on --
    items: {
      type: Array,
    },
    itemsProperty: {
      type: String,
    },
    useRangeHelp: {
      type: Boolean,
      default: false,
    },
    rangePrecision: {
      type: Number,
      default: 3,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    readonly: {
      type: Boolean,
      default: false,
    },
  },
  created() {
    this.onQuery = (query) => {
      this.query = query;
    };
    this.simputChannel.$on('query', this.onQuery);

    this.onUpdateUI = () => {
      const newValue = `__${this.name}__${this.uiTS()}`;
      if (this.tsKey !== newValue) {
        this.$nextTick(() => {
          this.tsKey = newValue;
        });
      }
    };
    this.simputChannel.$on('templateTS', this.onUpdateUI);
    this.onUpdateUI();
  },
  beforeDestroy() {
    this.simputChannel.$off('query', this.onQuery);
    this.simputChannel.$off('templateTS', this.onUpdateUI);
  },
  data() {
    return {
      showHelp: false,
      tsKey: '__default__',
      query: '',
    };
  },
  computed: {
    ...COMPUTED.query,
    ...COMPUTED.decorator,
    ...COMPUTED.convert,
    textToQuery() {
      return `${this.name?.toLowerCase() || ''} ${this.label?.toLowerCase() ||
        ''} ${this.help?.toLowerCase() || ''} ${JSON.stringify(
        this.computedItems
      )}`;
    },
    model: {
      get() {
        /* eslint-disable no-unused-expressions */
        this.mtime; // force refresh
        return this.properties() && this.properties()[this.name];
      },
      set(v) {
        this.properties()[this.name] = v;
      },
    },
    multiple() {
      return Number(this.size) === -1;
    },
    computedItems() {
      if (this.items) {
        return this.items;
      }
      // Dynamic domain evaluation
      if (this.itemsProperty) {
        const available =
          this.domains()[this.itemsProperty]?.LabelList?.available || [];
        const filteredValues = this.properties()[this.itemsProperty];
        return addLabels(filteredValues, available);
      }
      const availableOptions = this.domains()[this.name] || {};

      return (
        availableOptions?.List?.available ||
        availableOptions?.HasTags?.available ||
        availableOptions?.ProxyBuilder?.available ||
        availableOptions?.FieldSelector?.available
      );
    },
    selectedItem() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return this.computedItems.find(({ value }) => value === this.model);
    },
    computedHelp() {
      if (!this.useRangeHelp) {
        return this.help;
      }
      if (this.selectedItem && this.selectedItem?.range) {
        const rangeStr = this.selectedItem.range
          .map((v) => v.toFixed(this.rangePrecision))
          .join(', ');
        if (this.help) {
          return `${this.help} - [${rangeStr}]`;
        }
        return `[${rangeStr}]`;
      }
      return this.help;
    },
  },
  methods: {
    validate() {
      if (this.multiple || Array.isArray(this.model)) {
        this.model = this.model.map((v) => this.convert(v));
      } else {
        this.model = this.convert(this.model);
      }
      this.dirty(this.name);
    },
  },
  inject: ['data', 'properties', 'domains', 'dirty', 'uiTS', 'simputChannel'],
};
