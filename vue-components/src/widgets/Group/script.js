import { COMPUTED } from '../../core/utils';

export default {
  name: 'swGroup',
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
  data() {
    return {
      mounted: false,
    };
  },
  mounted() {
    // We need to be monted to know about our visibility
    this.mounted = true;
  },
  computed: {
    ...COMPUTED.decorator,
    visible() {
      this.mtime; // eslint-disable-line
      this.mounted; // eslint-disable-line

      if (this.decorator && !this.decorator.show && !this.decorator.query) {
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
      this.$slots.default?.forEach(helper);
      return visibleCount > 0;
    },
  },
  inject: ['domains'],
};
