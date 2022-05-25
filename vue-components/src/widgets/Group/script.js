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
      this.$slots.default.forEach((vNode) => {
        const show =
          vNode.componentInstance?.shouldShow ||
          vNode.componentInstance?.decorator?.show;
        if (show) {
          visibleCount++;
        }
      });
      return visibleCount > 0;
    },
  },
  inject: ['domains'],
};
