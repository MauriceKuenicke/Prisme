<template>
  <svg
    class="line-icon"
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    :stroke="color"
    :stroke-width="strokeWidth"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <component
      :is="node.tag"
      v-for="(node, index) in iconNodes"
      :key="`${name}-${index}`"
      v-bind="node.attrs"
    />
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  size: {
    type: [String, Number],
    default: 18
  },
  strokeWidth: {
    type: [String, Number],
    default: 1.8
  },
  color: {
    type: String,
    default: 'currentColor'
  }
})

const ICONS = {
  x: [
    { tag: 'line', attrs: { x1: '18', y1: '6', x2: '6', y2: '18' } },
    { tag: 'line', attrs: { x1: '6', y1: '6', x2: '18', y2: '18' } }
  ],
  trash: [
    { tag: 'path', attrs: { d: 'M3 6h18' } },
    { tag: 'path', attrs: { d: 'M8 6V4h8v2' } },
    { tag: 'path', attrs: { d: 'M19 6l-1 14H6L5 6' } },
    { tag: 'line', attrs: { x1: '10', y1: '11', x2: '10', y2: '17' } },
    { tag: 'line', attrs: { x1: '14', y1: '11', x2: '14', y2: '17' } }
  ],
  pencil: [
    { tag: 'path', attrs: { d: 'M12 20h9' } },
    { tag: 'path', attrs: { d: 'M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4 11.5-11.5z' } }
  ],
  eye: [
    { tag: 'path', attrs: { d: 'M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6z' } },
    { tag: 'circle', attrs: { cx: '12', cy: '12', r: '3' } }
  ],
  file: [
    { tag: 'path', attrs: { d: 'M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7z' } },
    { tag: 'path', attrs: { d: 'M14 2v5h5' } },
    { tag: 'line', attrs: { x1: '9', y1: '13', x2: '15', y2: '13' } },
    { tag: 'line', attrs: { x1: '9', y1: '17', x2: '15', y2: '17' } }
  ],
  copy: [
    { tag: 'rect', attrs: { x: '9', y: '9', width: '11', height: '11', rx: '2', ry: '2' } },
    { tag: 'path', attrs: { d: 'M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1' } }
  ],
  plus: [
    { tag: 'line', attrs: { x1: '12', y1: '5', x2: '12', y2: '19' } },
    { tag: 'line', attrs: { x1: '5', y1: '12', x2: '19', y2: '12' } }
  ],
  clock: [
    { tag: 'circle', attrs: { cx: '12', cy: '12', r: '9' } },
    { tag: 'path', attrs: { d: 'M12 7v5l3 2' } }
  ],
  check: [
    { tag: 'path', attrs: { d: 'M20 6L9 17l-5-5' } }
  ]
}

const iconNodes = computed(() => ICONS[props.name] || ICONS.x)
</script>

<style scoped>
.line-icon {
  display: inline-block;
  flex-shrink: 0;
  vertical-align: middle;
}
</style>
