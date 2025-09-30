package cmd

import (
	"errors"
	"fmt"

	"subnetter/internal/client"

	"github.com/spf13/cobra"
)

var pVrfID, pCIDR, pStatus, pDesc string

var prefixCreateCmd = &cobra.Command{
	Use:   "create-prefix",
	Short: "Create a Prefix",
	RunE: func(cmd *cobra.Command, args []string) error {
		if pVrfID == "" || pCIDR == "" {
			return errors.New("--vrf-id and --cidr are required")
		}
		if pStatus == "" {
			pStatus = "active"
		}
		c := client.New(baseURL, idemKey)
		p, err := c.CreatePrefix(pVrfID, pCIDR, pStatus, pDesc)
		if err != nil {
			return err
		}
		fmt.Printf("Prefix created: %s  id=%s  vrf=%s  status=%s\n", p.CIDR, p.ID, p.VRFID, p.Status)
		return nil
	},
}

func init() {
	rootCmd.AddCommand(prefixCreateCmd)
	prefixCreateCmd.Flags().StringVar(&pVrfID, "vrf-id", "", "VRF UUID (required)")
	prefixCreateCmd.Flags().StringVar(&pCIDR, "cidr", "", "CIDR, e.g. 10.0.0.0/24 (required)")
	prefixCreateCmd.Flags().StringVar(&pStatus, "status", "active", "container|active|reserved")
	prefixCreateCmd.Flags().StringVar(&pDesc, "desc", "", "description")
}
