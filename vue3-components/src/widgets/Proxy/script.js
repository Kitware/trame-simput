import SimputInput from "../../components/SimputItem/index.vue";
import { useDecorator } from "../../core/utils";

const { computed, inject, toRef, ref } = window.Vue;

export default {
  name: "swProxy",
  props: {
    name: {
      type: String,
    },
    mtime: {
      type: Number,
    },
    size: {
      type: Number,
      default: 1,
    },
    sizeControl: {
      type: Boolean,
      default: false,
    },
    proxyType: {
      type: String,
    },
  },
  components: {
    SimputInput,
  },
  setup(props) {
    const data = inject("data");
    const dirty = inject("dirty");
    const domains = inject("domains");

    const { decorator } = useDecorator({
      domains,
      mtime: toRef(props.mtime),
      name: toRef(props.name),
    });

    const properties = inject("properties");

    const model = computed({
      get() {
        /* eslint-disable no-unused-expressions */
        props.mtime; // force refresh
        const value = properties() && properties()[props.name];
        if (!value && props.size > 1) {
          const emptyArray = [];
          emptyArray.length = props.size;
          return emptyArray;
        }
        return value;
      },
      set(v) {
        properties()[props.name] = v;
      },
    });

    const itemId = computed(() => {
      /* eslint-disable no-unused-expressions */
      props.mtime; // force refresh
      return properties()[props.name];
    });

    const computedLayout = computed(() => {
      /* eslint-disable no-unused-expressions */
      props.mtime; // force refresh
      return props.layout || domains()[props.name]?.UI?.layout || "vertical";
    });

    const computedSize = computed(() => {
      if (Number(props.size) !== 1) {
        return Math.max(props.size || 1, model.value.length || 0);
      }
      return Number(props.size);
    });

    const computedSizeControl = computed(() => {
      /* eslint-disable no-unused-expressions */
      props.mtime; // force refresh
      return props.sizeControl || domains()[props.name]?.UI?.sizeControl;
    });

    const deleteEntry = function deleteEntry(index) {
      if (computedSize.value > Number(props.size)) {
        model.value.splice(index, 1);
        dirty(props.name);
      }
    };

    const getComponentProps = function getComponentProps(index) {
      if (computedLayout.value === "vertical") {
        return { cols: 12 };
      }
      if (computedLayout.value === "l2") {
        return { cols: 6 };
      }
      if (computedLayout.value === "l3") {
        return { cols: 4 };
      }
      if (computedLayout.value === "l4") {
        return { cols: 3 };
      }
      if (computedLayout.value === "m3-half") {
        const attrs = { cols: 4 };
        if (index === 3) {
          attrs.offset = 4;
        }
        if (index === 5) {
          attrs.offset = 8;
        }
        return attrs;
      }
      return {};
    };

    return {
      itemId,
      decorator,
      model,
      computedLayout,
      computedSize,
      computedSizeControl,
      deleteEntry,
      getComponentProps,
    };
  },
};
