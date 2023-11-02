import { useDecorator } from "../../core/utils";
const { ref, computed, onMounted, inject, useSlots, toRef } = window.Vue;

export default {
  name: "swGroup",
  props: {
    title: {
      type: String,
    },
    name: {
      type: String,
    },
    mtime: {
      type: Number,
    },
  },
  setup(props) {
    const mounted = ref(false);
    const domains = inject("domains");
    const slots = useSlots();

    const { decorator } = useDecorator({
      domains,
      mtime: toRef(props.mtime),
      name: toRef(props.name),
    });

    onMounted(() => (mounted.value = true));

    const visible = computed(() => {
      props.mtime; // eslint-disable-line
      mounted.value; // eslint-disable-line

      if (decorator.value && !decorator.value.show && !decorator.value.query) {
        return false;
      }

      let visibleCount = 0;
      const helper = (vNode) => {
        // if there is no component associated with this slot
        // look recursively in its children elements.
        // This can happen in the case of a nested group
        if (vNode.componentInstance == null) {
          vNode?.children?.forEach(helper);
        }
        const show =
          vNode.componentInstance?.shouldShow ||
          vNode.componentInstance?.decorator?.show;
        if (show) {
          visibleCount++;
        }
      };

      slots.default().forEach(helper);
      return visibleCount > 0;
    });

    return {
      visible,
    };
  },
};
