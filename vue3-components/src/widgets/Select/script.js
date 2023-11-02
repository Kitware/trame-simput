import { useQuery, useDecorator, useConvert } from "../../core/utils";
const { ref, computed, onMounted, onBeforeUnmount, inject, nextTick, toRef } =
  window.Vue;

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
  name: "swSelect",
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
  setup(props) {
    const domains = inject("domains");
    const query = ref("");

    const { decorator } = useDecorator({
      domains,
      mtime: toRef(props.mtime),
      name: toRef(props.name),
    });

    const { shouldShow } = useQuery({
      query,
      label: toRef(props.label),
      name: toRef(props.name),
      decorator,
    });

    const { convert } = useConvert({ type: toRef(props.type) });

    const data = inject("data");
    const properties = inject("properties");
    const dirty = inject("dirty");
    const uiTS = inject("uiTS");
    const simputChannel = inject("simputChannel");

    const showHelp = ref(false);
    const tsKey = ref("__default__");

    const onQuery = function onQuery(query) {
      query.value = query;
    };

    const onUpdateUI = function onUpdateUI() {
      const newValue = `__${props.name}__${uiTS()}`;
      if (tsKey.value !== newValue) {
        nextTick(() => {
          tsKey.value = newValue;
        });
      }
    };

    onMounted(() => {
      simputChannel.$on("query", onQuery);
      simputChannel.$on("templateTS", onUpdateUI);
      onUpdateUI();
    });

    onBeforeUnmount(() => {
      simputChannel.$off("query", onQuery);
      simputChannel.$off("templateTS", onUpdateUI);
    });

    const model = computed({
      get() {
        /* eslint-disable no-unused-expressions */
        props.mtime; // force refresh
        return properties() && properties()[props.name];
      },
      set(v) {
        properties()[props.name] = v;
      },
    });

    const multiple = computed(() => {
      return Number(props.size) === -1;
    });

    // METHODS
    const validate = function validate() {
      if (multiple.value || Array.isArray(model.value)) {
        model.value = model.value.map((v) => convert.value(v));
      } else {
        model.value = convert.value(model.value);
      }
      dirty(props.name);
    };

    const computedItems = computed(() => {
      if (props.items) {
        return props.items;
      }
      // Dynamic domain evaluation
      if (props.itemsProperty) {
        const available =
          domains()[props.itemsProperty]?.LabelList?.available || [];
        const filteredValues = properties()[props.itemsProperty];
        return addLabels(filteredValues, available);
      }
      const availableOptions = domains()[props.name] || {};

      return (
        availableOptions?.List?.available ||
        availableOptions?.HasTags?.available ||
        availableOptions?.ProxyBuilder?.available ||
        availableOptions?.FieldSelector?.available
      );
    });

    const textToQuery = computed(() => {
      return `${props.name?.toLowerCase() || ""} ${
        props.label?.toLowerCase() || ""
      } ${props.help?.toLowerCase() || ""} ${JSON.stringify(
        computedItems.value
      )}`;
    });

    const selectedItem = computed(() => {
      /* eslint-disable no-unused-expressions */
      props.mtime; // force refresh
      return computedItems.find(({ value }) => value === model.value);
    });

    const computedHelp = computed(() => {
      if (!props.useRangeHelp) {
        return props.help;
      }
      if (selectedItem.value && selectedItem.value?.range) {
        const rangeStr = selectedItem.value.range
          .map((v) => v.toFixed(props.rangePrecision))
          .join(", ");
        if (props.help) {
          return `${props.help} - [${rangeStr}]`;
        }
        return `[${rangeStr}]`;
      }
      return props.help;
    });

    return {
      tsKey,
      computedHelp,
      model,
      computedItems,
      multiple,
      validate,
      decorator,
      shouldShow,
    };
  },
};
