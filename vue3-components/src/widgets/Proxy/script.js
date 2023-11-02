import SimputInput from "../../components/SimputItem/index.vue";
import { useDecorator } from "../../core/utils";

const { computed, inject, toRef } = window.Vue;

export default {
  name: "swProxy",
  props: {
    name: {
      type: String,
    },
    mtime: {
      type: Number,
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
    const itemId = computed(() => {
      /* eslint-disable no-unused-expressions */
      props.mtime; // force refresh
      return properties()[props.name];
    });

    return {
      itemId,
      decorator,
    };
  },
};
