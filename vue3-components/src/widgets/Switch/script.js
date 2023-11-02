import { useQuery, useDecorator, useConvert } from "../../core/utils";
const { ref, computed, onMounted, onBeforeUnmount, inject, toRef } = window.Vue;

export default {
  name: "swSwitch",
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
    const showHelp = ref(false);
    const query = ref("");
    const domains = inject("domains");

    const simputChannel = inject("simputChannel");
    const properties = inject("properties");
    const dirty = inject("dirty");

    const { decorator } = useDecorator({
      domains,
      mtime: toRef(props.mtime),
      name: toRef(props.name),
    });

    const { shouldShow, textToQuery } = useQuery({
      query,
      label: toRef(props.label),
      name: toRef(props.name),
      decorator,
    });

    const { convert } = useConvert({ type: toRef(props.type) });

    const onQuery = function onQuery(query) {
      query.value = query;
    };

    onMounted(() => {
      simputChannel.$on("query", onQuery);
    });

    onBeforeUnmount(() => {
      simputChannel.$off("query", onQuery);
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

    const validate = function validate() {
      model.value = convert.value(model.value);
      dirty(props.name);
    };

    return {
      validate,
      showHelp,
      decorator,
      model,
      shouldShow,
    };
  },
};
