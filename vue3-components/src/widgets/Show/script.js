const { computed, inject } = window.Vue;

export default {
  name: "swShow",
  props: {
    property: {
      type: String,
    },
    domain: {
      type: String,
    },
    mtime: {
      type: Number,
    },
  },
  setup(props) {
    const properties = inject("properties");
    const domains = inject("domains");

    const visible = computed(() => {
      this.mtime; // eslint-disable-line
      const domain = domains()?.[props.property]?.[props.domain];
      if (!domain) {
        // no domain == valid
        return true;
      }
      return domain.value.value;
    });

    return {
      visible,
    };
  },
};
